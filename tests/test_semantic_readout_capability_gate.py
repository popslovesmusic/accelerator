import json
import os
import unittest
from pathlib import Path
from unittest import mock

from scripts import query_governance as qg
from tools.signal_scope_phase_continuation_engine.core import semantic_readout as sr


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "registry" / "db" / "acellorator_index.sqlite"
TASK_NAME = "PATCH_ACCELERATOR_SEMANTIC_READOUT_CAPABILITY_GATE_051"


REPLY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_id",
        "schema_version",
        "reply_text",
        "reply_source",
        "backend_status",
        "authorization_reason",
        "caller_id",
        "purpose_code",
        "capsule_hash",
        "fallback_used",
        "telemetry_event_id",
    ],
    "properties": {
        "schema_id": {"const": "semantic_readout_reply_v1"},
        "schema_version": {"const": "1.0.0"},
        "reply_text": {"type": "string"},
        "reply_source": {"enum": ["LOCAL_DETERMINISTIC", "NETWORK_MODEL"]},
        "summary_id": {"type": ["string", "null"]},
        "backend_status": {"enum": ["NOT_REQUESTED", "DENIED", "SUCCESS", "FAILED"]},
        "authorization_reason": {"type": "string"},
        "caller_id": {"type": "string"},
        "purpose_code": {"type": "string"},
        "capsule_hash": {"type": "string"},
        "fallback_used": {"type": "boolean"},
        "telemetry_event_id": {"type": "string"},
    },
}


TELEMETRY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "event_type",
        "event_id",
        "timestamp",
        "caller_id",
        "purpose_code",
        "capability_enabled",
        "configured_backend",
        "model_id",
        "authorization_result",
        "authorization_reason",
        "capsule_hash",
        "projection_hash",
        "input_bytes",
        "estimated_input_tokens",
        "actual_input_tokens_if_reported",
        "actual_output_tokens_if_reported",
        "requested_output_limit",
        "latency_ms",
        "network_attempted",
        "outcome",
        "fallback_used",
        "error_class",
        "retry_count",
    ],
    "properties": {
        "event_type": {
            "enum": [
                "BOUNDARY_EVALUATED",
                "BOUNDARY_DENIED",
                "NETWORK_REQUEST_STARTED",
                "NETWORK_REQUEST_SUCCEEDED",
                "NETWORK_REQUEST_FAILED",
                "LOCAL_REPLY_RETURNED",
            ]
        },
        "event_id": {"type": "string"},
        "timestamp": {"type": "string"},
        "caller_id": {"type": "string"},
        "purpose_code": {"type": "string"},
        "capability_enabled": {"type": "boolean"},
        "configured_backend": {"type": "string"},
        "model_id": {"type": "string"},
        "authorization_result": {"type": "string"},
        "authorization_reason": {"type": "string"},
        "capsule_hash": {"type": "string"},
        "projection_hash": {"type": ["string", "null"]},
        "input_bytes": {"type": "integer"},
        "estimated_input_tokens": {"type": ["integer", "null"]},
        "actual_input_tokens_if_reported": {"type": ["integer", "null"]},
        "actual_output_tokens_if_reported": {"type": ["integer", "null"]},
        "requested_output_limit": {"type": ["integer", "null"]},
        "latency_ms": {"type": ["number", "null"]},
        "network_attempted": {"type": "boolean"},
        "outcome": {"type": "string"},
        "fallback_used": {"type": "boolean"},
        "error_class": {"type": ["string", "null"]},
        "retry_count": {"type": "integer"},
    },
}


class FakeHTTPResponse:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


class SemanticReadoutCapabilityGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid_capsule = qg.build_governed_context_capsule_v1(
            str(DB_PATH),
            task=TASK_NAME,
            use_cache=False,
        )
        cls.invalid_capsule = dict(cls.valid_capsule)
        cls.invalid_capsule["capsule_hash"] = "0" * 64
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

    def _config(self, **semantic_overrides):
        semantic_readout = {
            "enabled": True,
            "backend": "local",
            "style": "hs_science",
            "max_sentences": 4,
            "include_followup_question": True,
            "caution_hedge_threshold": 0.65,
            "hold_explain": True,
            "enable_network_semantic_readout": False,
            "telemetry_enabled": True,
            "log_prompt_content": False,
            "allowed_callers": [],
            "allowed_purposes": [],
            "allowed_network_endpoints": ["https://api.openai.com"],
            "retry_budget": 0,
            "network_retry_budget": 0,
            "openai_compatible": {
                "base_url": "https://api.openai.com",
                "model": "",
                "timeout_s": 12.0,
            },
        }
        for key, value in semantic_overrides.items():
            semantic_readout[key] = value
        return {"semantic_readout": semantic_readout}

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
            required = schema.get("required", [])
            for field in required:
                self.assertIn(field, instance, f"{path}.{field}")
            properties = schema.get("properties", {})
            for field, field_schema in properties.items():
                if field in instance:
                    self._assert_schema(instance[field], field_schema, f"{path}.{field}")
            if schema.get("additionalProperties") is False:
                self.assertSetEqual(set(instance.keys()), set(properties.keys()) | set(required), path)

        if schema_type == "array" or (isinstance(schema_type, list) and "array" in schema_type):
            self.assertIsInstance(instance, list, path)
            item_schema = schema.get("items")
            if item_schema is not None:
                for index, item in enumerate(instance):
                    self._assert_schema(item, item_schema, f"{path}[{index}]")

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
            return (isinstance(value, (int, float)) and not isinstance(value, bool))
        if expected_type == "null":
            return value is None
        return True

    def _assert_reply_schema(self, result):
        self._assert_schema(result, REPLY_SCHEMA)

    def _assert_event_schema(self, events):
        for event in events:
            self._assert_schema(event, TELEMETRY_SCHEMA)

    def test_default_local_reply_uses_no_network_and_preserves_string_api(self):
        events = []
        prompt = "What is gravity?"
        with mock.patch.object(sr.urllib.request, "urlopen", side_effect=AssertionError("network should not be called")) as mocked_urlopen:
            structured = sr.generate_structured_reply(
                prompt=prompt,
                runtime_output=self.runtime_output,
                config=None,
                telemetry_sink=events.append,
            )
            reply = sr.generate_reply(
                prompt=prompt,
                runtime_output=self.runtime_output,
                config=None,
            )

        self.assertEqual(mocked_urlopen.call_count, 0)
        self.assertEqual(structured["reply_source"], "LOCAL_DETERMINISTIC")
        self.assertEqual(structured["backend_status"], "NOT_REQUESTED")
        self.assertFalse(structured["fallback_used"])
        self.assertEqual(reply, structured["reply_text"])
        self._assert_reply_schema(structured)
        self.assertGreaterEqual(len(events), 2)
        self.assertIn("BOUNDARY_EVALUATED", {event["event_type"] for event in events})
        self.assertIn("LOCAL_REPLY_RETURNED", {event["event_type"] for event in events})
        self._assert_event_schema(events)

    def test_capability_disabled_denies_even_with_credentials(self):
        events = []
        config = self._config(
            backend="openai_compatible",
            enable_network_semantic_readout=False,
            openai_compatible={"base_url": "https://api.openai.com", "model": "gpt-test", "timeout_s": 3.0},
            allowed_callers=["analysis_intake.worker"],
            allowed_purposes=["HUMAN_READABLE_SUMMARY"],
            network_retry_budget=1,
            retry_budget=1,
        )
        with mock.patch.dict(os.environ, {"SEMANTIC_READOUT_API_KEY": "sk-test"}, clear=False):
            with mock.patch.object(sr.urllib.request, "urlopen", side_effect=AssertionError("network should not be called")) as mocked_urlopen:
                structured = sr.generate_structured_reply(
                    prompt="Summarize the runtime state.",
                    runtime_output=self.runtime_output,
                    config=config,
                    caller_id="analysis_intake.worker",
                    purpose_code="HUMAN_READABLE_SUMMARY",
                    governed_context_capsule=self.valid_capsule,
                    telemetry_sink=events.append,
                )

        self.assertEqual(mocked_urlopen.call_count, 0)
        self.assertEqual(structured["backend_status"], "NOT_REQUESTED")
        self.assertEqual(structured["authorization_reason"], "CAPABILITY_DISABLED")
        self.assertFalse(structured["fallback_used"])
        self._assert_reply_schema(structured)
        self.assertIn("BOUNDARY_EVALUATED", {event["event_type"] for event in events})
        self.assertIn("LOCAL_REPLY_RETURNED", {event["event_type"] for event in events})
        self.assertNotIn("NETWORK_REQUEST_STARTED", {event["event_type"] for event in events})
        self._assert_event_schema(events)

    def test_missing_caller_denied(self):
        events = []
        config = self._config(
            backend="openai_compatible",
            enable_network_semantic_readout=True,
            openai_compatible={"base_url": "https://api.openai.com", "model": "gpt-test", "timeout_s": 3.0},
            allowed_callers=["analysis_intake.worker"],
            allowed_purposes=["HUMAN_READABLE_SUMMARY"],
            network_retry_budget=1,
            retry_budget=1,
        )
        with mock.patch.dict(os.environ, {"SEMANTIC_READOUT_API_KEY": "sk-test"}, clear=False):
            with mock.patch.object(sr.urllib.request, "urlopen", side_effect=AssertionError("network should not be called")):
                structured = sr.generate_structured_reply(
                    prompt="Summarize the runtime state.",
                    runtime_output=self.runtime_output,
                    config=config,
                    caller_id=None,
                    purpose_code="HUMAN_READABLE_SUMMARY",
                    governed_context_capsule=self.valid_capsule,
                    telemetry_sink=events.append,
                )

        self.assertEqual(structured["backend_status"], "DENIED")
        self.assertEqual(structured["authorization_reason"], "CALLER_MISSING")
        self.assertTrue(structured["fallback_used"])
        self._assert_reply_schema(structured)
        self.assertIn("BOUNDARY_DENIED", {event["event_type"] for event in events})
        self.assertIn("LOCAL_REPLY_RETURNED", {event["event_type"] for event in events})
        self.assertNotIn("NETWORK_REQUEST_STARTED", {event["event_type"] for event in events})
        self._assert_event_schema(events)

    def test_invalid_capsule_hash_denied(self):
        events = []
        config = self._config(
            backend="openai_compatible",
            enable_network_semantic_readout=True,
            openai_compatible={"base_url": "https://api.openai.com", "model": "gpt-test", "timeout_s": 3.0},
            allowed_callers=["analysis_intake.worker"],
            allowed_purposes=["HUMAN_READABLE_SUMMARY"],
            network_retry_budget=1,
            retry_budget=1,
        )
        with mock.patch.dict(os.environ, {"SEMANTIC_READOUT_API_KEY": "sk-test"}, clear=False):
            with mock.patch.object(sr.urllib.request, "urlopen", side_effect=AssertionError("network should not be called")):
                structured = sr.generate_structured_reply(
                    prompt="Summarize the runtime state.",
                    runtime_output=self.runtime_output,
                    config=config,
                    caller_id="analysis_intake.worker",
                    purpose_code="HUMAN_READABLE_SUMMARY",
                    governed_context_capsule=self.invalid_capsule,
                    telemetry_sink=events.append,
                )

        self.assertEqual(structured["backend_status"], "DENIED")
        self.assertEqual(structured["authorization_reason"], "CAPSULE_HASH_INVALID")
        self.assertTrue(structured["fallback_used"])
        self._assert_reply_schema(structured)
        self.assertIn("BOUNDARY_DENIED", {event["event_type"] for event in events})
        self.assertIn("LOCAL_REPLY_RETURNED", {event["event_type"] for event in events})
        self._assert_event_schema(events)

    def test_missing_capsule_denied(self):
        events = []
        config = self._config(
            backend="openai_compatible",
            enable_network_semantic_readout=True,
            openai_compatible={"base_url": "https://api.openai.com", "model": "gpt-test", "timeout_s": 3.0},
            allowed_callers=["analysis_intake.worker"],
            allowed_purposes=["HUMAN_READABLE_SUMMARY"],
            network_retry_budget=1,
            retry_budget=1,
        )
        with mock.patch.dict(os.environ, {"SEMANTIC_READOUT_API_KEY": "sk-test"}, clear=False):
            with mock.patch.object(sr.urllib.request, "urlopen", side_effect=AssertionError("network should not be called")):
                structured = sr.generate_structured_reply(
                    prompt="Summarize the runtime state.",
                    runtime_output=self.runtime_output,
                    config=config,
                    caller_id="analysis_intake.worker",
                    purpose_code="HUMAN_READABLE_SUMMARY",
                    governed_context_capsule=None,
                    telemetry_sink=events.append,
                )

        self.assertEqual(structured["backend_status"], "DENIED")
        self.assertEqual(structured["authorization_reason"], "CAPSULE_MISSING")
        self.assertTrue(structured["fallback_used"])
        self._assert_reply_schema(structured)
        self.assertIn("BOUNDARY_DENIED", {event["event_type"] for event in events})
        self.assertIn("LOCAL_REPLY_RETURNED", {event["event_type"] for event in events})
        self._assert_event_schema(events)

    def test_authorized_network_success_single_request_and_schema(self):
        events = []
        config = self._config(
            backend="openai_compatible",
            enable_network_semantic_readout=True,
            openai_compatible={"base_url": "https://api.openai.com", "model": "gpt-test", "timeout_s": 3.0},
            allowed_callers=["analysis_intake.worker"],
            allowed_purposes=["HUMAN_READABLE_SUMMARY"],
            network_retry_budget=1,
            retry_budget=1,
        )
        fake_payload = {
            "id": "chatcmpl-test-001",
            "choices": [{"message": {"content": "Network reply."}}],
            "usage": {"prompt_tokens": 11, "completion_tokens": 5},
        }
        with mock.patch.dict(os.environ, {"SEMANTIC_READOUT_API_KEY": "sk-test"}, clear=False):
            with mock.patch.object(sr.urllib.request, "urlopen", return_value=FakeHTTPResponse(fake_payload)) as mocked_urlopen:
                structured = sr.generate_structured_reply(
                    prompt="Summarize the runtime state.",
                    runtime_output=self.runtime_output,
                    config=config,
                    caller_id="analysis_intake.worker",
                    purpose_code="HUMAN_READABLE_SUMMARY",
                    governed_context_capsule=self.valid_capsule,
                    telemetry_sink=events.append,
                )

        self.assertEqual(mocked_urlopen.call_count, 1)
        self.assertEqual(structured["reply_source"], "NETWORK_MODEL")
        self.assertEqual(structured["backend_status"], "SUCCESS")
        self.assertFalse(structured["fallback_used"])
        self.assertEqual(structured["authorization_reason"], "AUTHORIZED")
        self._assert_reply_schema(structured)
        self.assertIn("BOUNDARY_EVALUATED", {event["event_type"] for event in events})
        self.assertIn("NETWORK_REQUEST_STARTED", {event["event_type"] for event in events})
        self.assertIn("NETWORK_REQUEST_SUCCEEDED", {event["event_type"] for event in events})
        self.assertNotIn("LOCAL_REPLY_RETURNED", {event["event_type"] for event in events})
        self._assert_event_schema(events)
        serialized_events = json.dumps(events, sort_keys=True)
        self.assertNotIn("sk-test", serialized_events)
        self.assertNotIn("Summarize the runtime state.", serialized_events)

    def test_network_failure_falls_back_without_retry(self):
        events = []
        config = self._config(
            backend="openai_compatible",
            enable_network_semantic_readout=True,
            openai_compatible={"base_url": "https://api.openai.com", "model": "gpt-test", "timeout_s": 3.0},
            allowed_callers=["analysis_intake.worker"],
            allowed_purposes=["HUMAN_READABLE_SUMMARY"],
            network_retry_budget=1,
            retry_budget=1,
        )
        with mock.patch.dict(os.environ, {"SEMANTIC_READOUT_API_KEY": "sk-test"}, clear=False):
            with mock.patch.object(sr.urllib.request, "urlopen", side_effect=sr.urllib.error.URLError("boom")) as mocked_urlopen:
                structured = sr.generate_structured_reply(
                    prompt="Summarize the runtime state.",
                    runtime_output=self.runtime_output,
                    config=config,
                    caller_id="analysis_intake.worker",
                    purpose_code="HUMAN_READABLE_SUMMARY",
                    governed_context_capsule=self.valid_capsule,
                    telemetry_sink=events.append,
                )

        self.assertEqual(mocked_urlopen.call_count, 1)
        self.assertEqual(structured["reply_source"], "LOCAL_DETERMINISTIC")
        self.assertEqual(structured["backend_status"], "FAILED")
        self.assertTrue(structured["fallback_used"])
        self.assertEqual(structured["authorization_reason"], "AUTHORIZED")
        self._assert_reply_schema(structured)
        event_types = {event["event_type"] for event in events}
        self.assertIn("BOUNDARY_EVALUATED", event_types)
        self.assertIn("NETWORK_REQUEST_STARTED", event_types)
        self.assertIn("NETWORK_REQUEST_FAILED", event_types)
        self.assertIn("LOCAL_REPLY_RETURNED", event_types)
        self._assert_event_schema(events)


if __name__ == "__main__":
    unittest.main()
