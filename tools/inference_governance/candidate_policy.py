from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from .request_normalization import hash_json_value, normalize_identifier, normalize_identifier_list, normalize_text, normalize_tree


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OPERATION_REGISTRY_PATH = ROOT / "registry" / "deterministic_operation_registry.json"
DEFAULT_CANDIDATE_POLICY_REGISTRY_PATH = ROOT / "registry" / "candidate_policy_registry.json"
CANDIDATE_POLICY_REGISTRY_SCHEMA_ID = "candidate_policy_registry_v1"
CANDIDATE_POLICY_REGISTRY_SCHEMA_VERSION = "1.0.0"
CANDIDATE_POLICY_SCHEMA_ID = "candidate_policy_v1"
CANDIDATE_POLICY_SCHEMA_VERSION = "1.0.0"
BOUND_CANDIDATE_SET_SCHEMA_ID = "bounded_candidate_set_v1"
BOUND_CANDIDATE_SET_SCHEMA_VERSION = "1.0.0"
DEFAULT_CANDIDATE_LIMIT = 20
DEFAULT_RANKING_METHOD = "rank_score_then_candidate_id"
DEFAULT_TIE_BEHAVIOR = "candidate_id"
DEFAULT_EMPTY_SET_BEHAVIOR = "EMPTY_RESULT"

DEFAULT_CANDIDATE_POLICY_REGISTRY = {
    "schema_id": CANDIDATE_POLICY_REGISTRY_SCHEMA_ID,
    "schema_version": CANDIDATE_POLICY_REGISTRY_SCHEMA_VERSION,
    "policies": [
        {
            "candidate_policy_id": "governed_context_artifact_candidates_v1",
            "candidate_type": "ARTIFACT",
            "universe_source": "registry/db/acellorator_index.sqlite:artifacts",
            "eligibility_filters": ["query_match", "authority", "freshness", "scope", "compatibility"],
            "authority_filters": ["authority_scope"],
            "freshness_filters": ["indexed_at", "db_snapshot_status"],
            "scope_filters": ["target", "focus_query"],
            "compatibility_filters": ["orientation_status"],
            "ranking_method": "score_then_path",
            "maximum_candidates": 20,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        },
        {
            "candidate_policy_id": "registry_runtime_trace_candidates_v1",
            "candidate_type": "ARTIFACT",
            "universe_source": "registry/db/acellorator_index.sqlite:artifacts+tool_health",
            "eligibility_filters": ["query_match", "authority", "freshness", "scope", "compatibility"],
            "authority_filters": ["authority_scope"],
            "freshness_filters": ["indexed_at", "evidence_source_path"],
            "scope_filters": ["query", "tool_name"],
            "compatibility_filters": ["orientation_status", "tool_health_status"],
            "ranking_method": "score_then_path",
            "maximum_candidates": 20,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        },
        {
            "candidate_policy_id": "governed_context_action_candidates_v1",
            "candidate_type": "ACTION",
            "universe_source": "scripts.query_governance._build_governed_context_candidate_actions",
            "eligibility_filters": ["governed_state"],
            "authority_filters": ["authority.decision"],
            "freshness_filters": ["freshness.db_snapshot_status"],
            "scope_filters": ["current_state.status", "patch_chain.status"],
            "compatibility_filters": ["priority", "trigger"],
            "ranking_method": "priority_then_action_id",
            "maximum_candidates": 8,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "action_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        },
        {
            "candidate_policy_id": "execution_plan_action_candidates_v1",
            "candidate_type": "ACTION",
            "universe_source": "scripts.orientation_execution_plan.generate_execution_plan",
            "eligibility_filters": ["query_substring", "retrieval_result"],
            "authority_filters": ["db_health.status"],
            "freshness_filters": ["retrieval.warnings"],
            "scope_filters": ["query"],
            "compatibility_filters": ["action_type"],
            "ranking_method": "priority_then_action_id",
            "maximum_candidates": 4,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "action_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        },
        {
            "candidate_policy_id": "residue_packet_artifact_candidates_v1",
            "candidate_type": "ARTIFACT",
            "universe_source": "scripts.residue.residue_packet_builder.build_residue_packet",
            "eligibility_filters": ["query_match", "authority", "freshness"],
            "authority_filters": ["authority_scope"],
            "freshness_filters": ["indexed_at"],
            "scope_filters": ["query"],
            "compatibility_filters": ["orientation_status"],
            "ranking_method": "score_then_path",
            "maximum_candidates": 20,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        },
        {
            "candidate_policy_id": "tool_candidates_v1",
            "candidate_type": "TOOL",
            "universe_source": "registry/tool_manifest.json",
            "eligibility_filters": ["registry_present"],
            "authority_filters": ["certification_level"],
            "freshness_filters": ["last_seen"],
            "scope_filters": ["name"],
            "compatibility_filters": ["status"],
            "ranking_method": "rank_score_then_candidate_id",
            "maximum_candidates": 256,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        },
        {
            "candidate_policy_id": "handler_candidates_v1",
            "candidate_type": "HANDLER",
            "universe_source": "registry/deterministic_operation_registry.json",
            "eligibility_filters": ["registry_present"],
            "authority_filters": ["authority_class"],
            "freshness_filters": ["policy_version"],
            "scope_filters": ["operation_code"],
            "compatibility_filters": ["status"],
            "ranking_method": "rank_score_then_candidate_id",
            "maximum_candidates": 64,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        },
        {
            "candidate_policy_id": "file_candidates_v1",
            "candidate_type": "FILE",
            "universe_source": "repository_file_index",
            "eligibility_filters": ["path_match", "authority", "freshness"],
            "authority_filters": ["authority_scope"],
            "freshness_filters": ["indexed_at", "last_modified"],
            "scope_filters": ["path", "target"],
            "compatibility_filters": ["status"],
            "ranking_method": "path_then_candidate_id",
            "maximum_candidates": 512,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        },
        {
            "candidate_policy_id": "validator_candidates_v1",
            "candidate_type": "VALIDATOR",
            "universe_source": "registry/governance/schemas",
            "eligibility_filters": ["schema_present"],
            "authority_filters": ["schema_version"],
            "freshness_filters": ["last_modified"],
            "scope_filters": ["schema_id"],
            "compatibility_filters": ["status"],
            "ranking_method": "rank_score_then_candidate_id",
            "maximum_candidates": 64,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        },
        {
            "candidate_policy_id": "output_template_candidates_v1",
            "candidate_type": "OUTPUT_TEMPLATE",
            "universe_source": "registry/governance/schemas",
            "eligibility_filters": ["schema_present"],
            "authority_filters": ["schema_version"],
            "freshness_filters": ["last_modified"],
            "scope_filters": ["schema_id"],
            "compatibility_filters": ["status"],
            "ranking_method": "rank_score_then_candidate_id",
            "maximum_candidates": 64,
            "empty_set_behavior": "EMPTY_RESULT",
            "tie_behavior": "candidate_id",
            "policy_version": "1.0.0",
            "status": "ACTIVE",
        },
    ],
}


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def load_candidate_policy_registry(path: str | Path | None = None) -> Dict[str, Any]:
    registry_path = Path(path) if path is not None else DEFAULT_CANDIDATE_POLICY_REGISTRY_PATH
    if registry_path.exists():
        try:
            return _load_json(registry_path)
        except (OSError, json.JSONDecodeError):
            pass
    return dict(DEFAULT_CANDIDATE_POLICY_REGISTRY)


def validate_candidate_policy_registry_payload(payload: Mapping[str, Any]) -> list[str]:
    result = dict(payload or {})
    errors: list[str] = []
    if normalize_identifier(result.get("schema_id")) != CANDIDATE_POLICY_REGISTRY_SCHEMA_ID:
        errors.append("schema_id_mismatch")
    if normalize_identifier(result.get("schema_version")) != CANDIDATE_POLICY_REGISTRY_SCHEMA_VERSION:
        errors.append("schema_version_mismatch")
    policies = result.get("policies")
    if not isinstance(policies, list):
        errors.append("policies_not_array")
        return errors
    required = {
        "candidate_policy_id",
        "candidate_type",
        "universe_source",
        "eligibility_filters",
        "authority_filters",
        "freshness_filters",
        "scope_filters",
        "compatibility_filters",
        "ranking_method",
        "maximum_candidates",
        "empty_set_behavior",
        "tie_behavior",
        "policy_version",
    }
    for index, policy in enumerate(policies):
        if not isinstance(policy, dict):
            errors.append(f"policy_not_object:{index}")
            continue
        missing = sorted(required - set(policy))
        for field in missing:
            errors.append(f"policy_missing_field:{index}:{field}")
    return errors


def build_candidate_policy_index(registry: Mapping[str, Any] | None = None) -> Dict[str, Dict[str, Any]]:
    payload = dict(registry or load_candidate_policy_registry())
    index: Dict[str, Dict[str, Any]] = {}
    for policy in payload.get("policies", []):
        if not isinstance(policy, dict):
            continue
        policy_id = normalize_identifier(policy.get("candidate_policy_id"), lowercase=True)
        if not policy_id:
            continue
        entry = {
            "candidate_policy_id": policy_id,
            "candidate_type": normalize_identifier(policy.get("candidate_type"), uppercase=True),
            "universe_source": normalize_identifier(policy.get("universe_source")),
            "eligibility_filters": normalize_identifier_list(policy.get("eligibility_filters")),
            "authority_filters": normalize_identifier_list(policy.get("authority_filters")),
            "freshness_filters": normalize_identifier_list(policy.get("freshness_filters")),
            "scope_filters": normalize_identifier_list(policy.get("scope_filters")),
            "compatibility_filters": normalize_identifier_list(policy.get("compatibility_filters")),
            "ranking_method": normalize_identifier(policy.get("ranking_method"), lowercase=True) or DEFAULT_RANKING_METHOD,
            "maximum_candidates": max(0, int(policy.get("maximum_candidates", DEFAULT_CANDIDATE_LIMIT) or DEFAULT_CANDIDATE_LIMIT)),
            "empty_set_behavior": normalize_identifier(policy.get("empty_set_behavior")) or DEFAULT_EMPTY_SET_BEHAVIOR,
            "tie_behavior": normalize_identifier(policy.get("tie_behavior"), lowercase=True) or DEFAULT_TIE_BEHAVIOR,
            "policy_version": normalize_identifier(policy.get("policy_version")) or CANDIDATE_POLICY_REGISTRY_SCHEMA_VERSION,
            "status": normalize_identifier(policy.get("status"), uppercase=True) or "ACTIVE",
        }
        index[policy_id] = entry
    return index


def get_candidate_policy(policy_id: str, registry: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    policy_index = build_candidate_policy_index(registry)
    normalized_id = normalize_identifier(policy_id, lowercase=True)
    policy = dict(policy_index.get(normalized_id, {}))
    if policy:
        return policy
    return {
        "candidate_policy_id": normalized_id,
        "candidate_type": "UNKNOWN",
        "universe_source": "",
        "eligibility_filters": [],
        "authority_filters": [],
        "freshness_filters": [],
        "scope_filters": [],
        "compatibility_filters": [],
        "ranking_method": DEFAULT_RANKING_METHOD,
        "maximum_candidates": DEFAULT_CANDIDATE_LIMIT,
        "empty_set_behavior": DEFAULT_EMPTY_SET_BEHAVIOR,
        "tie_behavior": DEFAULT_TIE_BEHAVIOR,
        "policy_version": CANDIDATE_POLICY_REGISTRY_SCHEMA_VERSION,
        "status": "UNKNOWN",
    }


def hash_candidate_universe(candidates: Sequence[Mapping[str, Any]], *, candidate_type: str, candidate_policy_id: str, policy_version: str) -> str:
    universe_basis = {
        "candidate_type": normalize_identifier(candidate_type, uppercase=True),
        "candidate_policy_id": normalize_identifier(candidate_policy_id, lowercase=True),
        "policy_version": normalize_identifier(policy_version),
        "candidates": [
            {
                "candidate_id": normalize_identifier(candidate.get("candidate_id")),
                "canonical_name": normalize_identifier(candidate.get("canonical_name")),
                "eligibility_status": normalize_identifier(candidate.get("eligibility_status"), uppercase=True),
                "authority_status": normalize_identifier(candidate.get("authority_status"), uppercase=True),
                "freshness_status": normalize_identifier(candidate.get("freshness_status"), uppercase=True),
                "compatibility_status": normalize_identifier(candidate.get("compatibility_status"), uppercase=True),
            }
            for candidate in candidates
            if isinstance(candidate, dict)
        ],
    }
    return hash_json_value(universe_basis)
