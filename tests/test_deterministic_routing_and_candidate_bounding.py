import json
import unittest
import re
import tempfile
from pathlib import Path

from scripts import query_governance as qg
from scripts.orientation_retrieval import retrieve_artifacts
from scripts.registry_runtime_trace import run_registry_runtime_trace
from tools.inference_governance.candidate_builder import build_bounded_candidate_set_v1
from tools.inference_governance.candidate_builder import resolve_candidate_set_v1
from tools.inference_governance.candidate_policy import (
    load_candidate_policy_registry,
    validate_candidate_policy_registry_payload,
)
from tools.inference_governance.deterministic_router import load_operation_registry, route_parsed_request
from tools.inference_governance.deterministic_router import validate_operation_registry_payload
from tools.inference_governance.request_normalization import (
    build_canonical_routed_request_v1,
    hash_canonical_routed_request,
)


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "registry" / "db" / "acellorator_index.sqlite"
SCHEMA_PATHS = {
    ROOT / "schemas" / "canonical_routed_request_v1.schema.json": "canonical_routed_request_v1",
    ROOT / "schemas" / "deterministic_operation_registry_v1.schema.json": "deterministic_operation_registry_v1",
    ROOT / "schemas" / "candidate_policy_registry_v1.schema.json": "candidate_policy_registry_v1",
    ROOT / "schemas" / "bounded_candidate_set_v1.schema.json": "bounded_candidate_set_v1",
}
ROUTER_ALLOWLIST = {
    "scripts/query_governance.py",
    "scripts/orientation_retrieval.py",
    "scripts/registry_runtime_trace.py",
    "scripts/orientation_execution_plan.py",
    "scripts/residue/residue_packet_builder.py",
    "tools/inference_governance/deterministic_router.py",
    "tools/signal_scope_phase_continuation_engine/core/semantic_readout.py",
}
ROUTER_CONTROL_PATTERN = re.compile(r"\b(?:if|elif)\b[^\n]*\b(?:request_type|surface_name|command)\b", re.IGNORECASE)
ROUTER_HANDLER_PATTERN = re.compile(
    r"\b(?:retrieve_artifacts|run_registry_runtime_trace|generate_execution_plan|build_residue_packet|build_governed_context_capsule_v1)\s*\(",
    re.IGNORECASE,
)
CANDIDATE_ALLOWLIST = {
    "scripts/orientation_retrieval.py",
    "scripts/registry_runtime_trace.py",
    "scripts/orientation_execution_plan.py",
    "scripts/residue/residue_packet_builder.py",
    "tools/inference_governance/candidate_builder.py",
}
CANDIDATE_ENUMERATION_PATTERN = re.compile(r"\b(?:rglob|glob|os\.walk|os\.listdir|iterdir)\s*\(", re.IGNORECASE)
CANDIDATE_DISCOVERY_PATTERN = re.compile(r"\b(?:candidate|universe|selection)\b", re.IGNORECASE)


def _relative_or_absolute(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _scan_for_router_violations(paths):
    violations = []
    for base in paths:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            rel = _relative_or_absolute(path)
            if rel in ROUTER_ALLOWLIST or rel.startswith("tests/"):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if ROUTER_CONTROL_PATTERN.search(text) and ROUTER_HANDLER_PATTERN.search(text):
                violations.append(rel)
    return sorted(dict.fromkeys(violations))


def _scan_for_candidate_violations(paths):
    violations = []
    for base in paths:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            rel = _relative_or_absolute(path)
            if rel in CANDIDATE_ALLOWLIST or rel.startswith("tests/"):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if CANDIDATE_ENUMERATION_PATTERN.search(text) and CANDIDATE_DISCOVERY_PATTERN.search(text):
                violations.append(rel)
    return sorted(dict.fromkeys(violations))


class DeterministicRoutingAndCandidateBoundingTests(unittest.TestCase):
    def test_governed_context_capsule_task_and_query_converge(self):
        task_capsule = qg.build_governed_context_capsule_v1(str(DB_PATH), task="registry", use_cache=False)
        query_capsule = qg.build_governed_context_capsule_v1(str(DB_PATH), query="registry", use_cache=False)

        self.assertEqual(task_capsule["capsule_hash"], query_capsule["capsule_hash"])
        self.assertEqual(task_capsule["request_identity"]["candidate_set_hash"], query_capsule["request_identity"]["candidate_set_hash"])

    def test_canonical_request_hash_ignores_presentation_only_fields(self):
        base = build_canonical_routed_request_v1(
            operation_code="artifact_retrieval",
            target_scope={
                "db_path": str(DB_PATH),
                "target": None,
                "focus_query": "foo",
                "limit": 5,
            },
            target_identifiers=["foo"],
            constraints={
                "db_path": str(DB_PATH),
                "limit": 5,
            },
            authority_requirements={
                "surface": "artifact_retrieval",
                "target": None,
            },
            freshness_requirements={
                "surface": "artifact_retrieval",
                "limit": 5,
            },
            output_contract={
                "schema_id": "orientation_retrieval_v1",
                "schema_version": "1.0.0",
            },
            presentation_preferences={
                "theme": "plain",
            },
            candidate_policy_id="governed_context_artifact_candidates_v1",
            source_request_digest="digest-a",
            normalization_record={
                "trace_id": "trace-a",
            },
            request_id="request-a",
        )
        variant = build_canonical_routed_request_v1(
            operation_code="artifact_retrieval",
            target_scope={
                "db_path": str(DB_PATH),
                "target": None,
                "focus_query": "foo",
                "limit": 5,
            },
            target_identifiers=["foo"],
            constraints={
                "db_path": str(DB_PATH),
                "limit": 5,
            },
            authority_requirements={
                "surface": "artifact_retrieval",
                "target": None,
            },
            freshness_requirements={
                "surface": "artifact_retrieval",
                "limit": 5,
            },
            output_contract={
                "schema_id": "orientation_retrieval_v1",
                "schema_version": "1.0.0",
            },
            presentation_preferences={
                "theme": "dense",
            },
            candidate_policy_id="governed_context_artifact_candidates_v1",
            source_request_digest="digest-b",
            normalization_record={
                "trace_id": "trace-b",
            },
            request_id="request-b",
        )

        self.assertEqual(hash_canonical_routed_request(base), hash_canonical_routed_request(variant))

    def test_route_parsed_request_aliases_and_unknown_operations(self):
        registry = load_operation_registry()
        capsule = {
            "authority": {
                "authority_status": "ALLOW",
            },
            "freshness": {
                "db_snapshot_status": "fresh",
            },
        }

        orientation_route = route_parsed_request(
            {
                "surface_name": "orientation_retrieval",
                "request_type": "orientation_retrieval",
                "db_path": str(DB_PATH),
                "query": "foo",
            },
            registry,
            capsule,
            "tests.deterministic_routing",
        )
        memory_route = route_parsed_request(
            {
                "surface_name": "memory_retrieval",
                "request_type": "memory_retrieval",
                "db_path": str(DB_PATH),
                "query": "foo",
            },
            registry,
            capsule,
            "tests.deterministic_routing",
        )
        unknown_route = route_parsed_request(
            {
                "surface_name": "not_a_registered_operation",
                "request_type": "not_a_registered_operation",
                "db_path": str(DB_PATH),
            },
            registry,
            capsule,
            "tests.deterministic_routing",
        )

        self.assertEqual(orientation_route["route_status"], "ROUTED")
        self.assertEqual(memory_route["route_status"], "ROUTED")
        self.assertEqual(orientation_route["operation_code"], "artifact_retrieval")
        self.assertEqual(memory_route["operation_code"], "artifact_retrieval")
        self.assertEqual(orientation_route["candidate_policy_id"], "governed_context_artifact_candidates_v1")
        self.assertEqual(memory_route["candidate_policy_id"], "governed_context_artifact_candidates_v1")
        self.assertEqual(unknown_route["route_status"], "ROUTE_UNRESOLVED")
        self.assertEqual(unknown_route["operation_code"], "")

    def test_registry_files_validate(self):
        operation_registry = load_operation_registry()
        candidate_registry = load_candidate_policy_registry()

        self.assertGreaterEqual(len(operation_registry.get("operations", [])), 1)
        self.assertGreaterEqual(len(candidate_registry.get("policies", [])), 1)
        self.assertEqual(validate_operation_registry_payload(operation_registry), [])
        self.assertEqual(validate_candidate_policy_registry_payload(candidate_registry), [])

    def test_schema_files_validate(self):
        for schema_path, schema_const in SCHEMA_PATHS.items():
            payload = json.loads(schema_path.read_text(encoding="utf-8"))
            self.assertIn("type", payload)
            self.assertEqual(payload["type"], "object")
            self.assertIn("required", payload)
            self.assertTrue(payload["required"], schema_path.as_posix())
            properties = payload.get("properties", {})
            self.assertIn("schema_id", properties, schema_path.as_posix())
            self.assertEqual(properties["schema_id"].get("const"), schema_const, schema_path.as_posix())

    def test_retrieval_and_trace_collapse_whitespace_variants(self):
        retrieval_base = retrieve_artifacts(str(DB_PATH), "foo", limit=5, explain=True)
        retrieval_variant = retrieve_artifacts(str(DB_PATH), " foo ", limit=5, explain=True)
        retrieval_upper = retrieve_artifacts(str(DB_PATH), "FOO", limit=5, explain=True)

        self.assertEqual(retrieval_base["candidate_set_hash"], retrieval_variant["candidate_set_hash"])
        self.assertEqual(retrieval_base["candidate_set_hash"], retrieval_upper["candidate_set_hash"])
        self.assertEqual(retrieval_base["candidate_policy_id"], retrieval_variant["candidate_policy_id"])
        self.assertEqual(retrieval_base["candidate_policy_id"], retrieval_upper["candidate_policy_id"])
        self.assertEqual([row["path"] for row in retrieval_base["results"]], [row["path"] for row in retrieval_variant["results"]])

        trace_base = run_registry_runtime_trace(str(DB_PATH), "foo", limit=5)
        trace_variant = run_registry_runtime_trace(str(DB_PATH), " foo ", limit=5)
        trace_artifacts_base = trace_base["trace_report"]["candidate_sets"]["artifacts"]
        trace_artifacts_variant = trace_variant["trace_report"]["candidate_sets"]["artifacts"]

        self.assertEqual(trace_artifacts_base["candidate_set_hash"], trace_artifacts_variant["candidate_set_hash"])
        self.assertEqual(
            [candidate["candidate_id"] for candidate in trace_artifacts_base["eligible_candidates"]],
            [candidate["candidate_id"] for candidate in trace_artifacts_variant["eligible_candidates"]],
        )

    def test_candidate_set_deduplicates_and_orders_deterministically(self):
        policy = {
            "candidate_policy_id": "unit_test_candidate_policy_v1",
            "candidate_type": "TOOL",
            "universe_source": "unit_test",
            "eligibility_filters": ["registry_present"],
            "authority_filters": ["authority"],
            "freshness_filters": ["freshness"],
            "scope_filters": ["scope"],
            "compatibility_filters": ["compatibility"],
            "ranking_method": "rank_score_then_candidate_id",
            "maximum_candidates": 10,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        }
        candidate_a = {
            "candidate_id": "B",
            "canonical_name": "B",
            "eligibility_status": "ELIGIBLE",
            "authority_status": "PASS",
            "freshness_status": "FRESH",
            "compatibility_status": "AVAILABLE",
            "rank_score": 1.0,
            "rank_components": {"order": 2},
            "provenance": {"source": "unit_test"},
        }
        candidate_b = dict(candidate_a, candidate_id="A", canonical_name="A", rank_components={"order": 1})
        duplicate_a = dict(candidate_b)

        set_a = build_bounded_candidate_set_v1(
            candidate_type="TOOL",
            candidate_policy=policy,
            universe_candidates=[candidate_a, candidate_b, duplicate_a],
            authority_hash="authority-one",
            freshness_hash="freshness-one",
            universe_hash="universe-one",
            operation_code="unit_test_operation",
            candidate_policy_id="unit_test_candidate_policy_v1",
            candidate_policy_version="1.0.0",
        )
        set_b = build_bounded_candidate_set_v1(
            candidate_type="TOOL",
            candidate_policy=policy,
            universe_candidates=[duplicate_a, candidate_a, candidate_b],
            authority_hash="authority-one",
            freshness_hash="freshness-one",
            universe_hash="universe-one",
            operation_code="unit_test_operation",
            candidate_policy_id="unit_test_candidate_policy_v1",
            candidate_policy_version="1.0.0",
        )
        set_authority_changed = build_bounded_candidate_set_v1(
            candidate_type="TOOL",
            candidate_policy=policy,
            universe_candidates=[candidate_a, candidate_b, duplicate_a],
            authority_hash="authority-two",
            freshness_hash="freshness-one",
            universe_hash="universe-one",
            operation_code="unit_test_operation",
            candidate_policy_id="unit_test_candidate_policy_v1",
            candidate_policy_version="1.0.0",
        )

        self.assertEqual(set_a["candidate_set_hash"], set_b["candidate_set_hash"])
        self.assertNotEqual(set_a["candidate_set_hash"], set_authority_changed["candidate_set_hash"])
        self.assertEqual([item["candidate_id"] for item in set_a["eligible_candidates"]], ["A", "B"])
        self.assertTrue(any(item["reason_code"] == "DUPLICATE_ALIAS" for item in set_a["excluded_candidates"]))

    def test_zero_candidate_resolution(self):
        policy = {
            "candidate_policy_id": "unit_test_candidate_policy_v1",
            "candidate_type": "TOOL",
            "universe_source": "unit_test",
            "eligibility_filters": ["registry_present"],
            "authority_filters": ["authority"],
            "freshness_filters": ["freshness"],
            "scope_filters": ["scope"],
            "compatibility_filters": ["compatibility"],
            "ranking_method": "rank_score_then_candidate_id",
            "maximum_candidates": 10,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        }
        empty_set = build_bounded_candidate_set_v1(
            candidate_type="TOOL",
            candidate_policy=policy,
            universe_candidates=[],
            authority_hash="authority-one",
            freshness_hash="freshness-one",
            universe_hash="universe-one",
            operation_code="unit_test_operation",
            candidate_policy_id="unit_test_candidate_policy_v1",
            candidate_policy_version="1.0.0",
        )

        resolution = resolve_candidate_set_v1(empty_set)
        self.assertEqual(resolution["resolution_status"], "DETERMINISTIC_NO_CANDIDATE")
        self.assertEqual(resolution["candidate_count"], 0)
        self.assertEqual(resolution["selected_candidate_id"], "")

    def test_single_candidate_resolution(self):
        policy = {
            "candidate_policy_id": "unit_test_candidate_policy_v1",
            "candidate_type": "TOOL",
            "universe_source": "unit_test",
            "eligibility_filters": ["registry_present"],
            "authority_filters": ["authority"],
            "freshness_filters": ["freshness"],
            "scope_filters": ["scope"],
            "compatibility_filters": ["compatibility"],
            "ranking_method": "rank_score_then_candidate_id",
            "maximum_candidates": 10,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        }
        single_candidate = {
            "candidate_id": "only",
            "canonical_name": "only",
            "eligibility_status": "ELIGIBLE",
            "authority_status": "PASS",
            "freshness_status": "FRESH",
            "compatibility_status": "AVAILABLE",
            "rank_score": 1.0,
            "rank_components": {"order": 1},
            "provenance": {"source": "unit_test"},
        }
        single_set = build_bounded_candidate_set_v1(
            candidate_type="TOOL",
            candidate_policy=policy,
            universe_candidates=[single_candidate],
            authority_hash="authority-one",
            freshness_hash="freshness-one",
            universe_hash="universe-one",
            operation_code="unit_test_operation",
            candidate_policy_id="unit_test_candidate_policy_v1",
            candidate_policy_version="1.0.0",
        )

        resolution = single_set["resolution"]
        self.assertEqual(resolution["resolution_status"], "DETERMINISTIC_SINGLE_CANDIDATE")
        self.assertEqual(resolution["candidate_count"], 1)
        self.assertEqual(resolution["selected_candidate_id"], "only")

    def test_dominant_candidate_resolution(self):
        policy = {
            "candidate_policy_id": "unit_test_candidate_policy_v1",
            "candidate_type": "TOOL",
            "universe_source": "unit_test",
            "eligibility_filters": ["registry_present"],
            "authority_filters": ["authority"],
            "freshness_filters": ["freshness"],
            "scope_filters": ["scope"],
            "compatibility_filters": ["compatibility"],
            "ranking_method": "rank_score_then_candidate_id",
            "maximum_candidates": 10,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        }
        dominant_candidate = {
            "candidate_id": "dominant",
            "canonical_name": "dominant",
            "eligibility_status": "ELIGIBLE",
            "authority_status": "PASS",
            "freshness_status": "FRESH",
            "compatibility_status": "AVAILABLE",
            "rank_score": 2.0,
            "rank_components": {"order": 1},
            "provenance": {"source": "unit_test"},
        }
        runner_up = dict(dominant_candidate, candidate_id="runner-up", canonical_name="runner-up", rank_score=1.0)
        dominant_set = build_bounded_candidate_set_v1(
            candidate_type="TOOL",
            candidate_policy=policy,
            universe_candidates=[runner_up, dominant_candidate],
            authority_hash="authority-one",
            freshness_hash="freshness-one",
            universe_hash="universe-one",
            operation_code="unit_test_operation",
            candidate_policy_id="unit_test_candidate_policy_v1",
            candidate_policy_version="1.0.0",
        )

        resolution = dominant_set["resolution"]
        self.assertEqual(resolution["resolution_status"], "DETERMINISTIC_TOP_CANDIDATE")
        self.assertEqual(resolution["candidate_count"], 2)
        self.assertEqual(resolution["selected_candidate_id"], "dominant")

    def test_bounded_gate_input_and_out_of_set_rejection(self):
        policy = {
            "candidate_policy_id": "unit_test_candidate_policy_v1",
            "candidate_type": "TOOL",
            "universe_source": "unit_test",
            "eligibility_filters": ["registry_present"],
            "authority_filters": ["authority"],
            "freshness_filters": ["freshness"],
            "scope_filters": ["scope"],
            "compatibility_filters": ["compatibility"],
            "ranking_method": "rank_score_then_candidate_id",
            "maximum_candidates": 10,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        }
        candidate = {
            "candidate_id": "A",
            "canonical_name": "A",
            "eligibility_status": "ELIGIBLE",
            "authority_status": "PASS",
            "freshness_status": "FRESH",
            "compatibility_status": "AVAILABLE",
            "rank_score": 1.0,
            "rank_components": {"order": 1},
            "provenance": {"source": "unit_test"},
        }
        bounded_set = build_bounded_candidate_set_v1(
            candidate_type="TOOL",
            candidate_policy=policy,
            universe_candidates=[candidate],
            authority_hash="authority-one",
            freshness_hash="freshness-one",
            universe_hash="universe-one",
            operation_code="unit_test_operation",
            candidate_policy_id="unit_test_candidate_policy_v1",
            candidate_policy_version="1.0.0",
        )

        self.assertEqual(bounded_set["candidate_set_hash"], bounded_set["candidate_set_hash"])
        self.assertEqual(bounded_set["candidate_count"], 1)
        self.assertEqual(bounded_set["resolution"]["resolution_status"], "DETERMINISTIC_SINGLE_CANDIDATE")

        rejected = resolve_candidate_set_v1(bounded_set, requested_candidate_id="missing")
        self.assertEqual(rejected["resolution_status"], "CANDIDATE_OUT_OF_SET")
        self.assertEqual(rejected["reason_code"], "OUT_OF_SET")
        self.assertEqual(rejected["selected_candidate_id"], "")

    def test_static_router_enforcement_detects_independent_router_violation(self):
        repo_violations = _scan_for_router_violations([ROOT / "scripts", ROOT / "tools"])
        self.assertEqual(repo_violations, [])

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            synthetic_router = temp_root / "synthetic_router.py"
            synthetic_router.write_text(
                "\n".join(
                    [
                        "from scripts.orientation_retrieval import retrieve_artifacts",
                        "",
                        "def route_request(request):",
                        "    if request.get('request_type') == 'artifact_retrieval':",
                        "        return retrieve_artifacts(request['db_path'], request.get('query'), limit=20)",
                        "    return None",
                    ]
                ),
                encoding="utf-8",
            )

            synthetic_violations = _scan_for_router_violations([temp_root])
            self.assertTrue(any(path.endswith("synthetic_router.py") for path in synthetic_violations))

    def test_static_unbounded_candidate_enforcement_detects_open_universe_violation(self):
        repo_violations = _scan_for_candidate_violations(
            [
                ROOT / "scripts" / "orientation_retrieval.py",
                ROOT / "scripts" / "registry_runtime_trace.py",
                ROOT / "scripts" / "orientation_execution_plan.py",
                ROOT / "scripts" / "residue" / "residue_packet_builder.py",
                ROOT / "tools" / "inference_governance" / "candidate_builder.py",
            ]
        )
        self.assertEqual(repo_violations, [])

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            synthetic_candidate = temp_root / "synthetic_candidate_builder.py"
            synthetic_candidate.write_text(
                "\n".join(
                    [
                        "from pathlib import Path",
                        "",
                        "def build_candidate_universe():",
                        "    return [str(path) for path in Path('.').rglob('*') if 'candidate' in path.name]",
                    ]
                ),
                encoding="utf-8",
            )

            synthetic_violations = _scan_for_candidate_violations([temp_root])
            self.assertTrue(any(path.endswith("synthetic_candidate_builder.py") for path in synthetic_violations))


if __name__ == "__main__":
    unittest.main()
