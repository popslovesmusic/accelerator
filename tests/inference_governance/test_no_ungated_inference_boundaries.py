import json
import os
import re
import unittest
from pathlib import Path
from unittest import mock

from scripts import query_governance as qg
from tools.inference_governance import evaluate_inference_necessity_gate, scan_repository_inference_boundaries
from tools.signal_scope_phase_continuation_engine.core import semantic_readout as sr


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "registry" / "db" / "acellorator_index.sqlite"
CONFIG_PATH = ROOT / "tools" / "signal_scope_phase_continuation_engine" / "config" / "config_v14_terminal.json"
REGISTRY_PATH = ROOT / "registry" / "inference_boundary_registry.json"
SEMANTIC_BOUNDARY_ID = "SEMANTIC_READOUT_OPTIONAL_OPENAI_001"
SOURCE_SCAN_ROOTS = [
    ROOT / "scripts",
    ROOT / "tools",
    ROOT / "tests",
    ROOT / "gpt_folder_bridge",
    ROOT / "departments",
]
REGISTERED_PROVIDER_PATHS = {
    "tools/signal_scope_phase_continuation_engine/core/semantic_readout.py",
}
DIRECT_PROVIDER_PATTERNS = {
    "urllib.request.urlopen(": re.compile(r"urllib\.request\.urlopen\s*\("),
    "chat.completions.create(": re.compile(r"chat\.completions\.create\s*\("),
    "responses.create(": re.compile(r"\bresponses\.create\s*\("),
    "generateContent(": re.compile(r"\bgenerateContent\s*\("),
    "OpenAI(": re.compile(r"\bOpenAI\s*\("),
    "Anthropic(": re.compile(r"\bAnthropic\s*\("),
}


GATE_EVENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "event_type",
        "event_id",
        "timestamp",
        "boundary_id",
        "caller_id",
        "purpose_code",
        "request_id",
        "capsule_hash",
        "decision",
        "reason_code",
        "authorized_mode",
        "deterministic_methods_considered",
        "deterministic_methods_executed",
        "remaining_uncertainty",
        "candidate_count",
        "effective_budget",
        "actual_calls",
        "actual_input_tokens",
        "actual_output_tokens",
        "latency_ms",
        "fallback_used",
        "error_class",
    ],
}


class InferenceNecessityGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.capsule = qg.build_governed_context_capsule_v1(
            str(DB_PATH),
            task="PATCH_ACCELERATOR_INFERENCE_NECESSITY_GATE_052",
            use_cache=False,
        )
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
        cls.network_config = {
            "semantic_readout": {
                "enabled": True,
                "backend": "openai_compatible",
                "style": "hs_science",
                "max_sentences": 4,
                "include_followup_question": True,
                "caution_hedge_threshold": 0.65,
                "hold_explain": True,
                "enable_network_semantic_readout": True,
                "telemetry_enabled": True,
                "log_prompt_content": False,
                "allowed_callers": ["analysis_intake.worker"],
                "allowed_purposes": ["HUMAN_READABLE_SUMMARY"],
                "allowed_network_endpoints": ["https://api.openai.com"],
                "retry_budget": 1,
                "network_retry_budget": 1,
                "openai_compatible": {
                    "base_url": "https://api.openai.com",
                    "model": "gpt-test",
                    "timeout_s": 3.0,
                },
            }
        }
        cls.deterministic_attempt_record = {
            "methods_considered": [
                "CONSTANT_CONFIGURATION",
                "LOOKUP",
                "CACHE",
                "RULE_ENGINE",
                "SCHEMA_VALIDATION",
                "ERROR_SIGNATURE_CLASSIFICATION",
            ],
            "methods_executed": [
                "CONSTANT_CONFIGURATION",
                "LOOKUP",
                "CACHE",
                "RULE_ENGINE",
                "SCHEMA_VALIDATION",
                "ERROR_SIGNATURE_CLASSIFICATION",
            ],
            "results": {
                "CONSTANT_CONFIGURATION": {"backend": "openai_compatible", "network_enabled": True},
                "LOOKUP": {"capsule_present": True, "capsule_reason": "CAPSULE_VALID", "capsule_valid": True},
                "CACHE": {"cache_answer_available": False, "cache_scope": "not used by semantic readout"},
                "RULE_ENGINE": {"caller_allowed": True, "purpose_allowed": True, "endpoint": "https://api.openai.com"},
                "SCHEMA_VALIDATION": {"capsule_errors": []},
                "ERROR_SIGNATURE_CLASSIFICATION": {
                    "selected_class": "class_1",
                    "confidence": 0.81,
                    "hold": True,
                },
            },
            "deterministic_answer_available": False,
            "cache_answer_available": False,
            "machine_readable_resolution_available": False,
            "finite_candidate_resolution_available": False,
            "failure_signature_resolution_available": False,
            "explanation": "The shared gate must decide whether optional semantic commentary is necessary after deterministic local readout and capsule validation.",
        }
        cls.uncertainty_record = {
            "uncertainty_id": "semantic-readout:analysis_intake.worker",
            "description": "The runtime summary retains unresolved orientation and caution structure beyond the local deterministic reply.",
            "materiality": "HIGH",
            "resolution_need": "OPTIONAL_PRESENTATION",
            "known_bounds": {
                "selected_class": "class_1",
                "confidence": 0.81,
                "caution": 0.42,
                "raw_caution": 0.18,
                "hold": True,
            },
            "unresolved_dimensions": ["selected_class", "confidence", "caution", "hold"],
            "consequence_of_no_inference": "Return the deterministic local reply and leave optional semantic commentary unresolved.",
        }
        cls.budget = {
            "maximum_calls": 1,
            "maximum_retries": 1,
            "maximum_input_tokens": 512,
            "maximum_output_tokens": 200,
            "maximum_latency_ms": 3000,
        }

    def _assert_schema(self, instance, schema, path="root"):
        if "const" in schema:
            self.assertEqual(instance, schema["const"], path)
            return
        schema_type = schema.get("type")
        if isinstance(schema_type, list):
            self.assertTrue(any(self._type_matches(instance, candidate) for candidate in schema_type), path)
        elif schema_type is not None:
            self.assertTrue(self._type_matches(instance, schema_type), path)
        if "enum" in schema:
            self.assertIn(instance, schema["enum"], path)
        if schema_type == "object" or (isinstance(schema_type, list) and "object" in schema_type):
            self.assertIsInstance(instance, dict, path)
            for field in schema.get("required", []):
                self.assertIn(field, instance, f"{path}.{field}")
        if schema_type == "array" or (isinstance(schema_type, list) and "array" in schema_type):
            self.assertIsInstance(instance, list, path)

    def _type_matches(self, value, expected_type):
        if expected_type == "object":
            return isinstance(value, dict)
        if expected_type == "array":
            return isinstance(value, list)
        if expected_type == "string":
            return isinstance(value, str)
        if expected_type == "boolean":
            return isinstance(value, bool)
        if expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if expected_type == "null":
            return value is None
        return True

    def test_boundary_registry_and_scan_are_consistent(self):
        scan = scan_repository_inference_boundaries(ROOT)

        self.assertEqual(scan["schema_id"], "inference_boundary_scan_v1")
        self.assertEqual(scan["summary"]["boundaries_found"], 1)
        self.assertEqual(scan["summary"]["test_only_surfaces"], 1)
        self.assertEqual(scan["summary"]["activation_surfaces"], 1)
        self.assertEqual(scan["summary"]["false_positives"], 1)
        self.assertEqual(scan["registry_errors"], [])
        self.assertEqual(scan["registered_boundaries"][0]["boundary_id"], SEMANTIC_BOUNDARY_ID)
        self.assertEqual(scan["registered_boundaries"][0]["status"], "LATENT")
        self.assertIn("analysis_intake.worker", scan["registered_boundaries"][0]["allowed_callers"])
        self.assertIn("HUMAN_READABLE_SUMMARY", scan["registered_boundaries"][0]["allowed_purposes"])
        self.assertEqual(scan["registered_boundaries"][0]["budget_ceiling"]["maximum_calls"], 1)
        self.assertEqual(scan["false_positives"][0]["path"], "gpt_folder_bridge/bridge.py")

    def test_repo_wide_direct_provider_invocations_are_allowlisted(self):
        matches = []
        for base in SOURCE_SCAN_ROOTS:
            if not base.exists():
                continue
            for path in base.rglob("*.py"):
                if path.resolve() == Path(__file__).resolve():
                    continue
                rel = path.relative_to(ROOT).as_posix()
                text = path.read_text(encoding="utf-8", errors="ignore")
                for name, pattern in DIRECT_PROVIDER_PATTERNS.items():
                    if pattern.search(text):
                        matches.append((rel, name))

        self.assertTrue(matches, "expected at least one registered provider invocation")
        for rel, pattern_name in matches:
            self.assertIn(rel, REGISTERED_PROVIDER_PATHS, f"ungated provider pattern {pattern_name} in {rel}")

    def test_shared_gate_denies_unknown_boundary_and_authorizes_registered_boundary(self):
        events = []

        denied = evaluate_inference_necessity_gate(
            boundary_id="UNKNOWN_BOUNDARY",
            caller_id="analysis_intake.worker",
            purpose_code="HUMAN_READABLE_SUMMARY",
            request_id="gate-test-unknown",
            governed_context_capsule=self.capsule,
            deterministic_attempt_record=self.deterministic_attempt_record,
            uncertainty_record=self.uncertainty_record,
            candidate_set=["openai_compatible"],
            inference_budget=self.budget,
            telemetry_sink=events.append,
        )

        self.assertFalse(denied["authorized"])
        self.assertEqual(denied["reason_code"], "DENY_BOUNDARY_NOT_REGISTERED")
        self.assertEqual({event["event_type"] for event in events}, {"GATE_EVALUATED", "GATE_DENIED"})
        for event in events:
            self._assert_schema(event, GATE_EVENT_SCHEMA)

        events.clear()
        authorized = evaluate_inference_necessity_gate(
            boundary_id=SEMANTIC_BOUNDARY_ID,
            caller_id="analysis_intake.worker",
            purpose_code="HUMAN_READABLE_SUMMARY",
            request_id="gate-test-authorized",
            governed_context_capsule=self.capsule,
            deterministic_attempt_record=self.deterministic_attempt_record,
            uncertainty_record=self.uncertainty_record,
            candidate_set=["openai_compatible"],
            inference_budget=self.budget,
            telemetry_sink=events.append,
        )

        self.assertTrue(authorized["authorized"])
        self.assertEqual(authorized["decision"], "AUTHORIZE_CONSTRAINED_INFERENCE")
        self.assertEqual(authorized["reason_code"], "AUTHORIZE_CONSTRAINED_INFERENCE")
        self.assertEqual(authorized["authorized_mode"], "CONSTRAINED")
        self.assertEqual(authorized["candidate_count"], 1)
        self.assertEqual(authorized["boundary_id"], SEMANTIC_BOUNDARY_ID)
        self.assertEqual(authorized["caller_id"], "analysis_intake.worker")
        self.assertEqual(authorized["purpose_code"], "HUMAN_READABLE_SUMMARY")
        self.assertEqual({event["event_type"] for event in events}, {"GATE_EVALUATED", "GATE_AUTHORIZED"})
        for event in events:
            self._assert_schema(event, GATE_EVENT_SCHEMA)

    def test_semantic_readout_uses_shared_gate_and_preserves_local_fallback(self):
        events = []
        prompt = "Summarize the runtime state."
        with mock.patch.object(sr, "evaluate_inference_necessity_gate", wraps=evaluate_inference_necessity_gate) as mocked_gate:
            with mock.patch.dict(os.environ, {"SEMANTIC_READOUT_API_KEY": "sk-test"}, clear=False):
                with mock.patch.object(
                    sr.urllib.request,
                    "urlopen",
                    return_value=type("FakeHTTPResponse", (), {
                        "__enter__": lambda self: self,
                        "__exit__": lambda self, exc_type, exc, tb: False,
                        "read": lambda self: json.dumps({
                            "id": "chatcmpl-test-001",
                            "choices": [{"message": {"content": "Network reply."}}],
                            "usage": {"prompt_tokens": 11, "completion_tokens": 5},
                        }).encode("utf-8"),
                    })(),
                ) as mocked_urlopen:
                    structured = sr.generate_structured_reply(
                        prompt=prompt,
                        runtime_output=self.runtime_output,
                        config=self.network_config,
                        caller_id="analysis_intake.worker",
                        purpose_code="HUMAN_READABLE_SUMMARY",
                        governed_context_capsule=self.capsule,
                        telemetry_sink=events.append,
                    )

        self.assertEqual(mocked_gate.call_count, 1)
        self.assertEqual(mocked_urlopen.call_count, 1)
        self.assertEqual(structured["reply_source"], "NETWORK_MODEL")
        self.assertEqual(structured["backend_status"], "SUCCESS")
        self.assertEqual(structured["authorization_reason"], "AUTHORIZED")
        self.assertFalse(structured["fallback_used"])
        self.assertIn("BOUNDARY_EVALUATED", {event["event_type"] for event in events})
        self.assertIn("NETWORK_REQUEST_STARTED", {event["event_type"] for event in events})
        self.assertIn("NETWORK_REQUEST_SUCCEEDED", {event["event_type"] for event in events})

    def test_config_defaults_remain_deterministic(self):
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        semantic = config["semantic_readout"]
        self.assertEqual(semantic["backend"], "local")
        self.assertFalse(semantic["enable_network_semantic_readout"])
        self.assertEqual(semantic["retry_budget"], 0)
        self.assertEqual(semantic["network_retry_budget"], 0)
        self.assertFalse(semantic["log_prompt_content"])


if __name__ == "__main__":
    unittest.main()
