import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import query_governance as qg
from tools.inference_governance import DecisionCacheStore, evaluate_inference_necessity_gate
from tools.inference_governance.cache_keys import build_semantic_readout_cache_context
from tools.inference_governance.cache_policy import (
    CLASS_A_DETERMINISTIC_RESULT,
    CLASS_B_ACCEPTED_CONSTRAINED_OUTPUT,
    CLASS_C_REJECTED_OR_FAILED_OUTPUT,
    CLASS_D_FORBIDDEN,
    REPLY_SOURCE_CACHED_ACCEPTED_OUTPUT,
    REPLY_SOURCE_CACHED_DETERMINISTIC,
)
from tools.signal_scope_phase_continuation_engine.core import semantic_readout as sr


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "registry" / "db" / "acellorator_index.sqlite"
TASK_NAME = "PATCH_ACCELERATOR_INFERENCE_NECESSITY_GATE_052"


class DecisionCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capsule = qg.build_governed_context_capsule_v1(
            str(DB_PATH),
            task=TASK_NAME,
            use_cache=False,
        )
        cls.invalid_capsule = dict(cls.capsule)
        cls.invalid_capsule["capsule_hash"] = "f" * 64
        cls.runtime_output = {
            "state": {
                "signature": {
                    "caution_scalar": 0.42,
                    "raw_caution_scalar": 0.18,
                    "recovery_scalar": 0.28,
                    "hold_state": True,
                    "active_component_id": "comp-12",
                    "components": ["north", "south"],
                },
                "orientation": {"active_operator": "northbound"},
                "reasoning": {"hold_semantics": "decay"},
            },
            "output": {
                "selected_class": "class_1",
                "confidence": 0.81,
            },
        }
        cls.prompt = "Summarize the runtime state."
        cls.caller_id = "analysis_intake.worker"
        cls.purpose_code = "HUMAN_READABLE_SUMMARY"
        cls.allowed_callers = [cls.caller_id]
        cls.allowed_purposes = [cls.purpose_code]
        cls.network_model = "gpt-test"

    def setUp(self):
        self._cache_dir = tempfile.TemporaryDirectory()
        self.cache_path = Path(self._cache_dir.name) / "decision_cache.sqlite3"
        self.store = DecisionCacheStore(self.cache_path)

    def tearDown(self):
        try:
            self._cache_dir.cleanup()
        except Exception:
            pass

    def _config(self, *, backend="local", enable_network=False, model="", allowed_callers=None, allowed_purposes=None):
        semantic_readout = {
            "enabled": True,
            "backend": backend,
            "style": "hs_science",
            "max_sentences": 4,
            "include_followup_question": True,
            "caution_hedge_threshold": 0.65,
            "hold_explain": True,
            "enable_network_semantic_readout": enable_network,
            "telemetry_enabled": True,
            "log_prompt_content": False,
            "allowed_callers": list(allowed_callers or []),
            "allowed_purposes": list(allowed_purposes or []),
            "allowed_network_endpoints": ["https://api.openai.com"],
            "retry_budget": 1 if enable_network else 0,
            "network_retry_budget": 1 if enable_network else 0,
            "decision_cache_path": str(self.cache_path),
            "openai_compatible": {
                "base_url": "https://api.openai.com",
                "model": model,
                "timeout_s": 3.0,
            },
        }
        return {"semantic_readout": semantic_readout}

    def _local_context(self, *, prompt=None, runtime_output=None, config=None, caller_id=None, purpose_code=None, capsule=None):
        return build_semantic_readout_cache_context(
            prompt=prompt or self.prompt,
            runtime_output=runtime_output or self.runtime_output,
            config=config or self._config(),
            caller_id=caller_id or self.caller_id,
            purpose_code=purpose_code or self.purpose_code,
            governed_context_capsule=capsule or self.capsule,
            candidate_ids=(),
            decision_type="semantic_readout.local_reply",
        )

    def _network_context(self, *, prompt=None, runtime_output=None, config=None, caller_id=None, purpose_code=None, capsule=None, candidate_ids=None):
        return build_semantic_readout_cache_context(
            prompt=prompt or self.prompt,
            runtime_output=runtime_output or self.runtime_output,
            config=config or self._config(backend="openai_compatible", enable_network=True, model=self.network_model, allowed_callers=self.allowed_callers, allowed_purposes=self.allowed_purposes),
            caller_id=caller_id or self.caller_id,
            purpose_code=purpose_code or self.purpose_code,
            governed_context_capsule=capsule or self.capsule,
            candidate_ids=candidate_ids or (self.network_model,),
            decision_type="semantic_readout.network_reply",
        )

    def _local_reply(self):
        return {
            "schema_id": "semantic_readout_reply_v1",
            "schema_version": "1.0.0",
            "reply_text": "Got it. Here's a short explanation and a quick state readback from the v14 engine. Engine snapshot: op=northbound comp=comp-12 caution=0.420 recovery=0.280 conf=0.810.",
            "reply_source": "LOCAL_DETERMINISTIC",
            "summary_id": None,
            "backend_status": "NOT_REQUESTED",
            "authorization_reason": "NOT_REQUESTED",
            "caller_id": self.caller_id,
            "purpose_code": self.purpose_code,
            "capsule_hash": self.capsule["capsule_hash"],
            "fallback_used": False,
            "telemetry_event_id": "evt-local",
        }

    def _network_reply(self):
        return {
            "schema_id": "semantic_readout_reply_v1",
            "schema_version": "1.0.0",
            "reply_text": "Network reply.",
            "reply_source": "NETWORK_MODEL",
            "summary_id": "chatcmpl-test-001",
            "backend_status": "SUCCESS",
            "authorization_reason": "AUTHORIZED",
            "caller_id": self.caller_id,
            "purpose_code": self.purpose_code,
            "capsule_hash": self.capsule["capsule_hash"],
            "fallback_used": False,
            "telemetry_event_id": "evt-network",
        }

    def _assert_raw_db_text(self, forbidden_values):
        with sqlite3.connect(str(self.cache_path)) as conn:
            rows = conn.execute(
                """
                SELECT request_semantics_json, cache_key_json, result_payload, validation_json, provenance_json
                FROM decision_cache_entries
                UNION ALL
                SELECT details_json, '', '', '', ''
                FROM decision_cache_events
                """
            ).fetchall()
        joined = "\n".join("\n".join(str(part or "") for part in row) for row in rows)
        for value in forbidden_values:
            self.assertNotIn(value, joined)

    def test_key_stability_and_incidental_request_ids_do_not_change_key(self):
        base = self._network_context()
        repeated = self._network_context()
        self.assertEqual(base["cache_key"], repeated["cache_key"])
        self.assertEqual(base["request_semantics_hash"], repeated["request_semantics_hash"])

        incidental_a = dict(base, request_id="request-001")
        incidental_b = dict(base, request_id="request-002")
        self.assertEqual(incidental_a["cache_key"], incidental_b["cache_key"])

    def test_key_changes_on_governed_dependency_change(self):
        base = self._network_context()

        authority_changed = self._network_context(
            config=self._config(
                backend="openai_compatible",
                enable_network=True,
                model=self.network_model,
                allowed_callers=["different.worker"],
                allowed_purposes=self.allowed_purposes,
            )
        )
        freshness_capsule = dict(self.capsule)
        freshness_capsule["freshness"] = dict(freshness_capsule.get("freshness", {}), state_revision="different")
        freshness_changed = self._network_context(capsule=freshness_capsule)
        capsule_changed = dict(self.capsule)
        capsule_changed["capsule_hash"] = "0" * 64
        capsule_changed_result = self._network_context(capsule=capsule_changed)
        candidate_changed = self._network_context(candidate_ids=("other-model",))
        policy_changed = build_semantic_readout_cache_context(
            prompt=self.prompt,
            runtime_output=self.runtime_output,
            config=self._config(
                backend="openai_compatible",
                enable_network=True,
                model=self.network_model,
                allowed_callers=self.allowed_callers,
                allowed_purposes=self.allowed_purposes,
            ),
            caller_id=self.caller_id,
            purpose_code=self.purpose_code,
            governed_context_capsule=self.capsule,
            candidate_ids=(self.network_model,),
            decision_type="semantic_readout.network_reply",
            boundary_policy_version="2.0.0",
        )
        validator_changed = build_semantic_readout_cache_context(
            prompt=self.prompt,
            runtime_output=self.runtime_output,
            config=self._config(
                backend="openai_compatible",
                enable_network=True,
                model=self.network_model,
                allowed_callers=self.allowed_callers,
                allowed_purposes=self.allowed_purposes,
            ),
            caller_id=self.caller_id,
            purpose_code=self.purpose_code,
            governed_context_capsule=self.capsule,
            candidate_ids=(self.network_model,),
            decision_type="semantic_readout.network_reply",
            validator_version="2.0.0",
        )
        schema_changed = build_semantic_readout_cache_context(
            prompt=self.prompt,
            runtime_output=self.runtime_output,
            config=self._config(
                backend="openai_compatible",
                enable_network=True,
                model=self.network_model,
                allowed_callers=self.allowed_callers,
                allowed_purposes=self.allowed_purposes,
            ),
            caller_id=self.caller_id,
            purpose_code=self.purpose_code,
            governed_context_capsule=self.capsule,
            candidate_ids=(self.network_model,),
            decision_type="semantic_readout.network_reply",
            output_schema_version="2.0.0",
        )

        comparisons = {
            "authority": authority_changed,
            "freshness": freshness_changed,
            "capsule": capsule_changed_result,
            "candidate": candidate_changed,
            "policy": policy_changed,
            "validator": validator_changed,
            "schema": schema_changed,
        }
        for name, context in comparisons.items():
            with self.subTest(name=name):
                self.assertNotEqual(base["cache_key"], context["cache_key"])

    def test_raw_model_output_forbidden(self):
        context = self._network_context()
        result = {
            "reply_text": "Free-form text without a schema wrapper.",
            "reply_source": "RAW_MODEL_PROSE",
            "backend_status": "SUCCESS",
            "authorization_reason": "AUTHORIZED",
            "caller_id": self.caller_id,
            "purpose_code": self.purpose_code,
            "capsule_hash": self.capsule["capsule_hash"],
            "fallback_used": False,
            "telemetry_event_id": "evt-raw",
        }
        written = self.store.store_result(context, result)
        self.assertFalse(written["written"])
        self.assertEqual(written["cache_class"], CLASS_D_FORBIDDEN)
        self.assertEqual(written["reason_code"], "RESULT_SCHEMA_INVALID")

    def test_deterministic_result_round_trip_hits_cache(self):
        context = self._local_context()
        write = self.store.store_result(context, self._local_reply())
        self.assertTrue(write["written"])
        self.assertEqual(write["cache_class"], CLASS_A_DETERMINISTIC_RESULT)

        lookup = self.store.lookup(context)
        self.assertTrue(lookup.hit)
        self.assertEqual(lookup.result["reply_source"], REPLY_SOURCE_CACHED_DETERMINISTIC)
        self.assertTrue(lookup.result["cache_hit"])

    def test_accepted_output_round_trip_hits_cache(self):
        context = self._network_context()
        write = self.store.store_result(context, self._network_reply())
        self.assertTrue(write["written"])
        self.assertEqual(write["cache_class"], CLASS_B_ACCEPTED_CONSTRAINED_OUTPUT)

        lookup = self.store.lookup(context)
        self.assertTrue(lookup.hit)
        self.assertEqual(lookup.result["reply_source"], REPLY_SOURCE_CACHED_ACCEPTED_OUTPUT)
        self.assertTrue(lookup.result["cache_hit"])

    def test_cache_miss_does_not_authorize_inference(self):
        context = self._network_context()
        gate = evaluate_inference_necessity_gate(
            boundary_id="SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
            caller_id=self.caller_id,
            purpose_code=self.purpose_code,
            request_id="cache-miss-test",
            governed_context_capsule=self.capsule,
            deterministic_attempt_record={
                "methods_considered": ["CACHE", "RULE_ENGINE"],
                "methods_executed": ["CACHE", "RULE_ENGINE"],
                "results": {"CACHE": {"cache_answer_available": False}},
                "deterministic_answer_available": False,
                "cache_answer_available": False,
                "machine_readable_resolution_available": False,
                "finite_candidate_resolution_available": False,
                "failure_signature_resolution_available": False,
                "explanation": "Cache miss does not decide the request.",
            },
            uncertainty_record={
                "uncertainty_id": "cache-miss",
                "description": "Material uncertainty remains.",
                "materiality": "HIGH",
                "resolution_need": "OPTIONAL_PRESENTATION",
                "known_bounds": {},
                "unresolved_dimensions": ["selection"],
                "consequence_of_no_inference": "No inference does not settle the request.",
            },
            candidate_set=["gpt-test"],
            inference_budget={
                "maximum_calls": 0,
                "maximum_retries": 0,
                "maximum_input_tokens": 0,
                "maximum_output_tokens": 0,
                "maximum_latency_ms": 0,
            },
            decision_cache_store=self.store,
            cache_request=context,
            telemetry_sink=None,
        )
        self.assertFalse(gate["cache_hit"])
        self.assertFalse(gate["authorized"])
        self.assertEqual(gate["decision"], "DENY_BUDGET_EXHAUSTED")

    def test_gate_short_circuits_on_accepted_output_cache_hit(self):
        context = self._network_context()
        self.store.store_result(context, self._network_reply())

        gate = evaluate_inference_necessity_gate(
            boundary_id="SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
            caller_id=self.caller_id,
            purpose_code=self.purpose_code,
            request_id="cache-hit-test",
            governed_context_capsule=self.capsule,
            deterministic_attempt_record={
                "methods_considered": ["CACHE", "RULE_ENGINE"],
                "methods_executed": ["CACHE", "RULE_ENGINE"],
                "results": {"CACHE": {"cache_answer_available": False}},
                "deterministic_answer_available": False,
                "cache_answer_available": False,
                "machine_readable_resolution_available": False,
                "finite_candidate_resolution_available": False,
                "failure_signature_resolution_available": False,
                "explanation": "Cache hit should short-circuit the inference branch.",
            },
            uncertainty_record={
                "uncertainty_id": "cache-hit",
                "description": "Material uncertainty remains.",
                "materiality": "HIGH",
                "resolution_need": "OPTIONAL_PRESENTATION",
                "known_bounds": {},
                "unresolved_dimensions": ["selection"],
                "consequence_of_no_inference": "No inference does not settle the request.",
            },
            candidate_set=["gpt-test"],
            inference_budget={
                "maximum_calls": 1,
                "maximum_retries": 1,
                "maximum_input_tokens": 1200,
                "maximum_output_tokens": 300,
                "maximum_latency_ms": 3000,
            },
            decision_cache_store=self.store,
            cache_request=context,
            telemetry_sink=None,
        )
        self.assertTrue(gate["cache_hit"])
        self.assertFalse(gate["authorized"])
        self.assertEqual(gate["decision"], "DENY_CACHE_RESULT_AVAILABLE")
        self.assertEqual(gate["cached_result"]["reply_source"], REPLY_SOURCE_CACHED_ACCEPTED_OUTPUT)

    def test_corrupt_payload_treated_as_miss(self):
        context = self._network_context()
        self.store.store_result(context, self._network_reply())
        with sqlite3.connect(str(self.cache_path)) as conn:
            conn.execute(
                "UPDATE decision_cache_entries SET result_payload = ? WHERE cache_key = ?",
                ("{not-json", context["cache_key"]),
            )
            conn.commit()

        lookup = self.store.lookup(context)
        self.assertFalse(lookup.hit)
        self.assertIn(lookup.reason_code, {"CACHE_REVALIDATION_FAILED", "CACHE_CORRUPT"})

    def test_hash_mismatch_treated_as_miss(self):
        context = self._network_context()
        self.store.store_result(context, self._network_reply())
        with sqlite3.connect(str(self.cache_path)) as conn:
            conn.execute(
                "UPDATE decision_cache_entries SET result_hash = ? WHERE cache_key = ?",
                ("0" * 64, context["cache_key"]),
            )
            conn.commit()

        lookup = self.store.lookup(context)
        self.assertFalse(lookup.hit)
        self.assertEqual(lookup.reason_code, "CACHE_CORRUPT")

    def test_semantic_readout_local_cache_reuse(self):
        events = []
        config = self._config()
        first = sr.generate_structured_reply(
            prompt=self.prompt,
            runtime_output=self.runtime_output,
            config=config,
            telemetry_sink=events.append,
        )
        second = sr.generate_structured_reply(
            prompt=self.prompt,
            runtime_output=self.runtime_output,
            config=config,
            telemetry_sink=events.append,
        )

        self.assertEqual(first["reply_source"], "LOCAL_DETERMINISTIC")
        self.assertEqual(second["reply_source"], REPLY_SOURCE_CACHED_DETERMINISTIC)
        self.assertTrue(second["cache_hit"])
        self.assertEqual(first["reply_text"], second["reply_text"])

    def test_semantic_readout_accepted_reuse_and_zero_followup_requests(self):
        events = []
        config = self._config(
            backend="openai_compatible",
            enable_network=True,
            model=self.network_model,
            allowed_callers=self.allowed_callers,
            allowed_purposes=self.allowed_purposes,
        )
        fake_payload = {
            "id": "chatcmpl-test-001",
            "choices": [{"message": {"content": "Network reply."}}],
            "usage": {"prompt_tokens": 11, "completion_tokens": 5},
        }
        with mock.patch.dict(os.environ, {"SEMANTIC_READOUT_API_KEY": "sk-test"}, clear=False):
            with mock.patch.object(sr.urllib.request, "urlopen", return_value=type("FakeHTTPResponse", (), {
                "__enter__": lambda self: self,
                "__exit__": lambda self, exc_type, exc, tb: False,
                "read": lambda self: __import__("json").dumps(fake_payload).encode("utf-8"),
            })()) as mocked_urlopen:
                first = sr.generate_structured_reply(
                    prompt=self.prompt,
                    runtime_output=self.runtime_output,
                    config=config,
                    caller_id=self.caller_id,
                    purpose_code=self.purpose_code,
                    governed_context_capsule=self.capsule,
                    telemetry_sink=events.append,
                )
        self.assertEqual(mocked_urlopen.call_count, 1)
        self.assertEqual(first["reply_source"], "NETWORK_MODEL")

        with mock.patch.dict(os.environ, {"SEMANTIC_READOUT_API_KEY": "sk-test"}, clear=False):
            with mock.patch.object(sr.urllib.request, "urlopen", side_effect=AssertionError("network should not be called")) as mocked_urlopen:
                second = sr.generate_structured_reply(
                    prompt=self.prompt,
                    runtime_output=self.runtime_output,
                    config=config,
                    caller_id=self.caller_id,
                    purpose_code=self.purpose_code,
                    governed_context_capsule=self.capsule,
                    telemetry_sink=events.append,
                )
        self.assertEqual(mocked_urlopen.call_count, 0)
        self.assertEqual(second["reply_source"], REPLY_SOURCE_CACHED_ACCEPTED_OUTPUT)
        self.assertTrue(second["cache_hit"])
        self.assertEqual(first["reply_text"], second["reply_text"])

    def test_no_secret_storage(self):
        config = self._config(
            backend="openai_compatible",
            enable_network=True,
            model=self.network_model,
            allowed_callers=self.allowed_callers,
            allowed_purposes=self.allowed_purposes,
        )
        fake_payload = {
            "id": "chatcmpl-test-001",
            "choices": [{"message": {"content": "Network reply."}}],
            "usage": {"prompt_tokens": 11, "completion_tokens": 5},
        }
        with mock.patch.dict(os.environ, {"SEMANTIC_READOUT_API_KEY": "sk-test"}, clear=False):
            with mock.patch.object(sr.urllib.request, "urlopen", return_value=type("FakeHTTPResponse", (), {
                "__enter__": lambda self: self,
                "__exit__": lambda self, exc_type, exc, tb: False,
                "read": lambda self: __import__("json").dumps(fake_payload).encode("utf-8"),
            })()):
                sr.generate_structured_reply(
                    prompt=self.prompt,
                    runtime_output=self.runtime_output,
                    config=config,
                    caller_id=self.caller_id,
                    purpose_code=self.purpose_code,
                    governed_context_capsule=self.capsule,
                )

        self._assert_raw_db_text(["sk-test", self.prompt])

    def test_advisory_authority_preserved(self):
        context = self._network_context()
        self.store.store_result(context, self._network_reply())
        gate = evaluate_inference_necessity_gate(
            boundary_id="SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
            caller_id=self.caller_id,
            purpose_code=self.purpose_code,
            request_id="authority-test",
            governed_context_capsule=self.capsule,
            deterministic_attempt_record={
                "methods_considered": ["CACHE", "RULE_ENGINE"],
                "methods_executed": ["CACHE", "RULE_ENGINE"],
                "results": {"CACHE": {"cache_answer_available": False}},
                "deterministic_answer_available": False,
                "cache_answer_available": False,
                "machine_readable_resolution_available": False,
                "finite_candidate_resolution_available": False,
                "failure_signature_resolution_available": False,
                "explanation": "Cache hit should not create execution authority.",
            },
            uncertainty_record={
                "uncertainty_id": "authority-test",
                "description": "Material uncertainty remains.",
                "materiality": "HIGH",
                "resolution_need": "OPTIONAL_PRESENTATION",
                "known_bounds": {},
                "unresolved_dimensions": ["selection"],
                "consequence_of_no_inference": "No inference does not settle the request.",
            },
            candidate_set=["gpt-test"],
            inference_budget={
                "maximum_calls": 1,
                "maximum_retries": 1,
                "maximum_input_tokens": 1200,
                "maximum_output_tokens": 300,
                "maximum_latency_ms": 3000,
            },
            decision_cache_store=self.store,
            cache_request=context,
            telemetry_sink=None,
        )
        self.assertFalse(gate["authorized"])
        self.assertEqual(gate["decision"], "DENY_CACHE_RESULT_AVAILABLE")
        self.assertEqual(gate["cached_result"]["reply_source"], REPLY_SOURCE_CACHED_ACCEPTED_OUTPUT)
        self.assertNotIn("authorized", gate["cached_result"])


if __name__ == "__main__":
    unittest.main()
