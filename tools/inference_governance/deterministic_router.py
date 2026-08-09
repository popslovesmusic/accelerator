from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from .candidate_policy import DEFAULT_OPERATION_REGISTRY_PATH, build_candidate_policy_index, get_candidate_policy, load_candidate_policy_registry, validate_candidate_policy_registry_payload
from .request_normalization import (
    build_canonical_routed_request_v1,
    canonical_request_surface_digest,
    hash_json_value,
    normalize_identifier,
    normalize_identifier_list,
    normalize_path_like,
    normalize_text,
    normalize_tree,
)


DEFAULT_ROUTE_STATUS = "ROUTE_UNRESOLVED"

DEFAULT_OPERATION_REGISTRY = {
    "schema_id": "deterministic_operation_registry_v1",
    "schema_version": "1.0.0",
    "operations": [
        {
            "operation_code": "governed_context_capsule",
            "canonical_name": "Governed Context Capsule",
            "aliases": [
                "context-capsule",
                "governed_context_capsule_v1",
                "current-state",
                "memory_context",
                "trace_context",
                "claim_context",
                "execution_context",
            ],
            "request_patterns": [
                {"field": "surface_name", "equals": "governed_context_capsule_v1"},
                {"field": "request_type", "equals": "governed_context_capsule"},
                {"field": "request_type", "equals": "memory_context"},
                {"field": "request_type", "equals": "trace_context"},
                {"field": "request_type", "equals": "claim_context"},
                {"field": "request_type", "equals": "execution_context"},
                {"field": "command", "equals": "context-capsule"},
            ],
            "required_fields": ["db_path"],
            "optional_fields": ["target", "task", "query", "limit"],
            "default_values": {"limit": 20},
            "candidate_policy_id": "governed_context_artifact_candidates_v1",
            "allowed_output_contracts": [
                "governed_context_capsule_v1",
                "gemini_trace_context_v1",
                "gemini_claim_context_v1",
                "gemini_execution_context_v1",
            ],
            "authority_class": "GOVERNED_CONTEXT",
            "freshness_policy": "CAPSULE_STATE",
            "handler_id": "scripts.query_governance.build_governed_context_capsule_v1",
            "fallback_behavior": "ROUTE_UNRESOLVED",
            "status": "ACTIVE",
        },
        {
            "operation_code": "artifact_retrieval",
            "canonical_name": "Artifact Retrieval",
            "aliases": [
                "orientation_retrieval",
                "artifact_lookup",
                "memory_retrieval",
                "residue_packet",
            ],
            "request_patterns": [
                {"field": "surface_name", "equals": "orientation_retrieval"},
                {"field": "surface_name", "equals": "memory_retrieval"},
                {"field": "surface_name", "equals": "residue_packet"},
                {"field": "request_type", "equals": "artifact_retrieval"},
                {"field": "request_type", "equals": "memory_retrieval"},
                {"field": "request_type", "equals": "residue_packet"},
            ],
            "required_fields": ["db_path"],
            "optional_fields": ["query", "status_filter", "limit"],
            "default_values": {"limit": 20},
            "candidate_policy_id": "governed_context_artifact_candidates_v1",
            "allowed_output_contracts": ["orientation_retrieval_v1", "memory_context_v1", "residue_packet_v1"],
            "authority_class": "READ_ONLY_CONTEXT",
            "freshness_policy": "ARTIFACT_ROWS",
            "handler_id": "scripts.orientation_retrieval.retrieve_artifacts",
            "fallback_behavior": "ROUTE_UNRESOLVED",
            "status": "ACTIVE",
        },
        {
            "operation_code": "registry_runtime_trace",
            "canonical_name": "Registry Runtime Trace",
            "aliases": ["runtime_trace", "trace_registry"],
            "request_patterns": [
                {"field": "surface_name", "equals": "registry_runtime_trace"},
                {"field": "request_type", "equals": "registry_runtime_trace"},
            ],
            "required_fields": ["db_path"],
            "optional_fields": ["query", "limit"],
            "default_values": {"limit": 20},
            "candidate_policy_id": "registry_runtime_trace_candidates_v1",
            "allowed_output_contracts": ["registry_runtime_trace_v1"],
            "authority_class": "READ_ONLY_CONTEXT",
            "freshness_policy": "RUNTIME_TRACE_ROWS",
            "handler_id": "scripts.registry_runtime_trace.run_registry_runtime_trace",
            "fallback_behavior": "ROUTE_UNRESOLVED",
            "status": "ACTIVE",
        },
        {
            "operation_code": "execution_plan",
            "canonical_name": "Execution Plan",
            "aliases": ["orientation_execution_plan"],
            "request_patterns": [
                {"field": "surface_name", "equals": "orientation_execution_plan"},
                {"field": "request_type", "equals": "execution_plan"},
            ],
            "required_fields": ["query", "db_path"],
            "optional_fields": ["limit"],
            "default_values": {"limit": 10},
            "candidate_policy_id": "execution_plan_action_candidates_v1",
            "allowed_output_contracts": ["orientation_execution_plan_v1"],
            "authority_class": "READ_ONLY_CONTEXT",
            "freshness_policy": "ARTIFACT_ROWS",
            "handler_id": "scripts.orientation_execution_plan.generate_execution_plan",
            "fallback_behavior": "ROUTE_UNRESOLVED",
            "status": "ACTIVE",
        },
        {
            "operation_code": "residue_packet",
            "canonical_name": "Residue Packet",
            "aliases": ["residue_packet_builder", "compress_residue"],
            "request_patterns": [
                {"field": "surface_name", "equals": "residue_packet_builder"},
                {"field": "request_type", "equals": "residue_packet"},
            ],
            "required_fields": ["query", "db_path"],
            "optional_fields": ["mode", "limit"],
            "default_values": {"limit": 20, "mode": "lossy_summary"},
            "candidate_policy_id": "residue_packet_artifact_candidates_v1",
            "allowed_output_contracts": ["residue_packet_v1"],
            "authority_class": "READ_ONLY_CONTEXT",
            "freshness_policy": "ARTIFACT_ROWS",
            "handler_id": "scripts.residue.residue_packet_builder.build_residue_packet",
            "fallback_behavior": "ROUTE_UNRESOLVED",
            "status": "ACTIVE",
        },
        {
            "operation_code": "legacy_lookup",
            "canonical_name": "Legacy Lookup Compatibility",
            "aliases": ["tech_note", "theorem", "tool", "claim", "open_gaps"],
            "request_patterns": [
                {"field": "request_type", "equals": "legacy_lookup"},
            ],
            "required_fields": ["db_path"],
            "optional_fields": ["tech_note", "theorem", "tool", "claim", "open_gaps"],
            "default_values": {},
            "candidate_policy_id": "governed_context_artifact_candidates_v1",
            "allowed_output_contracts": ["legacy_lookup_v1"],
            "authority_class": "READ_ONLY_CONTEXT",
            "freshness_policy": "ARTIFACT_ROWS",
            "handler_id": "scripts.query_governance.legacy_lookup",
            "fallback_behavior": "ROUTE_UNRESOLVED",
            "status": "ACTIVE",
        },
    ],
}


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def load_operation_registry(path: str | Path | None = None) -> Dict[str, Any]:
    registry_path = Path(path) if path is not None else DEFAULT_OPERATION_REGISTRY_PATH
    if registry_path.exists():
        try:
            return _load_json(registry_path)
        except (OSError, json.JSONDecodeError):
            pass
    return dict(DEFAULT_OPERATION_REGISTRY)


def validate_operation_registry_payload(payload: Mapping[str, Any]) -> list[str]:
    result = dict(payload or {})
    errors: list[str] = []
    if normalize_text(result.get("schema_id")) != "deterministic_operation_registry_v1":
        errors.append("schema_id_mismatch")
    if normalize_text(result.get("schema_version")) != "1.0.0":
        errors.append("schema_version_mismatch")
    operations = result.get("operations")
    if not isinstance(operations, list):
        errors.append("operations_not_array")
        return errors
    required = {
        "operation_code",
        "canonical_name",
        "aliases",
        "request_patterns",
        "required_fields",
        "optional_fields",
        "default_values",
        "candidate_policy_id",
        "allowed_output_contracts",
        "authority_class",
        "freshness_policy",
        "handler_id",
        "fallback_behavior",
        "status",
    }
    for index, operation in enumerate(operations):
        if not isinstance(operation, dict):
            errors.append(f"operation_not_object:{index}")
            continue
        missing = sorted(required - set(operation))
        for field in missing:
            errors.append(f"operation_missing_field:{index}:{field}")
    return errors


def build_operation_index(registry: Mapping[str, Any] | None = None) -> Dict[str, Dict[str, Any]]:
    payload = dict(registry or load_operation_registry())
    index: Dict[str, Dict[str, Any]] = {}
    for operation in payload.get("operations", []):
        if not isinstance(operation, dict):
            continue
        operation_code = normalize_text(operation.get("operation_code"), lowercase=True)
        if not operation_code:
            continue
        entry = {
            "operation_code": operation_code,
            "canonical_name": normalize_text(operation.get("canonical_name")),
            "aliases": normalize_identifier_list(operation.get("aliases"), lowercase=True),
            "request_patterns": [dict(pattern) for pattern in operation.get("request_patterns", []) if isinstance(pattern, dict)],
            "required_fields": normalize_identifier_list(operation.get("required_fields"), lowercase=True),
            "optional_fields": normalize_identifier_list(operation.get("optional_fields"), lowercase=True),
            "default_values": normalize_tree(operation.get("default_values", {})),
            "candidate_policy_id": normalize_text(operation.get("candidate_policy_id"), lowercase=True),
            "allowed_output_contracts": normalize_identifier_list(operation.get("allowed_output_contracts"), lowercase=True),
            "authority_class": normalize_text(operation.get("authority_class"), uppercase=True),
            "freshness_policy": normalize_text(operation.get("freshness_policy"), uppercase=True),
            "handler_id": normalize_text(operation.get("handler_id")),
            "fallback_behavior": normalize_text(operation.get("fallback_behavior"), uppercase=True),
            "status": normalize_text(operation.get("status"), uppercase=True),
        }
        index[operation_code] = entry
    return index


def _normalize_surface_request(parsed_request: Mapping[str, Any] | None) -> Dict[str, Any]:
    surface = dict(parsed_request or {})
    normalized = {
        "surface_name": normalize_text(surface.get("surface_name") or surface.get("command") or surface.get("request_type"), lowercase=True),
        "request_type": normalize_text(surface.get("request_type") or surface.get("surface_name") or surface.get("command"), lowercase=True),
        "command": normalize_text(surface.get("command"), lowercase=True),
        "operation_code": normalize_text(surface.get("operation_code") or surface.get("operation"), lowercase=True),
        "target": normalize_path_like(surface.get("target")) or normalize_text(surface.get("target")),
        "task": normalize_text(surface.get("task")),
        "query": normalize_text(surface.get("query")),
        "limit": surface.get("limit"),
        "status_filter": normalize_identifier_list(surface.get("status_filter"), lowercase=True),
        "candidate_ids": normalize_identifier_list(surface.get("candidate_ids"), lowercase=False),
        "exclusions": normalize_identifier_list(surface.get("exclusions"), lowercase=False),
    }
    return normalized


def _pattern_matches(pattern: Mapping[str, Any], request: Mapping[str, Any]) -> bool:
    field = normalize_text(pattern.get("field"), lowercase=True)
    if not field:
        return False
    value = request.get(field)
    equals = pattern.get("equals")
    contains = pattern.get("contains")
    casefold = bool(pattern.get("casefold", True))
    if isinstance(value, list):
        haystack = [normalize_text(item, lowercase=casefold) for item in value]
    else:
        haystack = normalize_text(value, lowercase=casefold)
    if equals is not None:
        expected = normalize_text(equals, lowercase=casefold)
        if isinstance(haystack, list):
            return expected in haystack
        return haystack == expected
    if contains is not None:
        expected = normalize_text(contains, lowercase=casefold)
        if isinstance(haystack, list):
            return any(expected in item for item in haystack)
        return expected in haystack
    return bool(haystack)


def _collect_matches(request: Mapping[str, Any], operation_index: Mapping[str, Dict[str, Any]]) -> list[Dict[str, Any]]:
    matches: list[Dict[str, Any]] = []
    for operation in operation_index.values():
        if operation.get("status") not in {"ACTIVE", "LATENT"}:
            continue
        explicit_tokens = {
            normalize_text(operation.get("operation_code"), lowercase=True),
            normalize_text(operation.get("handler_id"), lowercase=True),
            normalize_text(operation.get("canonical_name"), lowercase=True),
        }
        request_tokens = {
            normalize_text(request.get("operation_code"), lowercase=True),
            normalize_text(request.get("surface_name"), lowercase=True),
            normalize_text(request.get("request_type"), lowercase=True),
            normalize_text(request.get("command"), lowercase=True),
        }
        alias_tokens = set(operation.get("aliases", []))
        if request_tokens & explicit_tokens or request_tokens & alias_tokens:
            matches.append(
                {
                    "operation": operation,
                    "matched_rule_id": "explicit_token_match",
                    "precedence": 0,
                }
            )
            continue

        for index, pattern in enumerate(operation.get("request_patterns", [])):
            if _pattern_matches(pattern, request):
                matches.append(
                    {
                        "operation": operation,
                        "matched_rule_id": f"pattern:{pattern.get('field')}={pattern.get('equals', pattern.get('contains', 'present'))}",
                        "precedence": 10 + index,
                    }
                )
                break
    return matches


def route_parsed_request(
    parsed_request: Mapping[str, Any] | None,
    operation_registry: Mapping[str, Any] | None,
    governed_context_capsule: Mapping[str, Any] | None,
    caller_id: str | None,
) -> Dict[str, Any]:
    registry = dict(operation_registry or load_operation_registry())
    operation_index = build_operation_index(registry)
    request = _normalize_surface_request(parsed_request)
    request_digest = canonical_request_surface_digest(request)
    matches = _collect_matches(request, operation_index)

    selected_match = None
    if not matches:
        route_status = "ROUTE_UNRESOLVED"
        selected = {}
        ambiguity_record = {
            "match_count": 0,
            "matched_operation_codes": [],
            "caller_id": normalize_text(caller_id),
            "reason": "No registered operation matched the request surface.",
        }
    else:
        matches.sort(key=lambda item: (item["precedence"], normalize_text(item["operation"].get("operation_code"))))
        top_precedence = matches[0]["precedence"]
        top_matches = [item for item in matches if item["precedence"] == top_precedence]
        if len(top_matches) > 1:
            selected_match = top_matches[0]
            selected = selected_match["operation"]
            route_status = "ROUTE_AMBIGUOUS"
            ambiguity_record = {
                "match_count": len(matches),
                "matched_operation_codes": [item["operation"]["operation_code"] for item in matches],
                "selected_operation_code": selected["operation_code"],
                "caller_id": normalize_text(caller_id),
                "reason": "Multiple operations matched with the same precedence.",
            }
        else:
            selected_match = top_matches[0]
            selected = selected_match["operation"]
            route_status = "ROUTED"
            ambiguity_record = {
                "match_count": len(matches),
                "matched_operation_codes": [item["operation"]["operation_code"] for item in matches],
                "selected_operation_code": selected["operation_code"],
                "caller_id": normalize_text(caller_id),
                "reason": "Unique registered operation matched.",
            }

    operation_code = normalize_text(selected.get("operation_code"), lowercase=True) if selected else ""
    candidate_policy_id = normalize_text(selected.get("candidate_policy_id"), lowercase=True) if selected else ""
    handler_id = normalize_text(selected.get("handler_id")) if selected else ""
    defaults = dict(selected.get("default_values", {})) if selected else {}
    target_scope = {
        "surface_name": request.get("surface_name"),
        "request_type": request.get("request_type"),
        "command": request.get("command"),
        "target": request.get("target"),
        "task": request.get("task"),
        "query": request.get("query"),
        "limit": request.get("limit", defaults.get("limit")),
        "status_filter": request.get("status_filter"),
    }
    authority_requirements = {
        "authority_class": normalize_text(selected.get("authority_class"), uppercase=True),
        "caller_id": normalize_text(caller_id),
        "capsule_hash": normalize_text(_safe_capsule_lookup(governed_context_capsule, "capsule_hash")),
        "authority_status": normalize_text(_safe_capsule_lookup(governed_context_capsule, "authority", "authority_status"), uppercase=True),
    }
    freshness_requirements = {
        "freshness_policy": normalize_text(selected.get("freshness_policy"), uppercase=True),
        "freshness_status": normalize_text(_safe_capsule_lookup(governed_context_capsule, "freshness", "db_snapshot_status"), uppercase=True),
        "freshness_hash": normalize_text(_safe_capsule_lookup(governed_context_capsule, "freshness_hash")),
    }
    allowed_output_contracts = list(selected.get("allowed_output_contracts", [])) if selected else []
    first_output_contract = allowed_output_contracts[0] if allowed_output_contracts else ""
    output_contract = {
        "schema_id": normalize_text(_safe_output_contract(request, selected, "schema_id") or first_output_contract),
        "schema_version": normalize_text(_safe_output_contract(request, selected, "schema_version") or "1.0.0"),
        "output_type": normalize_text(_safe_output_contract(request, selected, "output_type") or first_output_contract),
    }
    presentation_preferences = {
        "surface_name": request.get("surface_name"),
        "command": request.get("command"),
        "request_type": request.get("request_type"),
        "source_request_digest": request_digest,
    }
    normalization_record = {
        "schema_id": "canonical_routed_request_v1",
        "schema_version": "1.0.0",
        "surface_request": request,
        "matched_rule_id": selected_match.get("matched_rule_id") if selected_match else None,
        "matched_precedence": matches[0]["precedence"] if matches else None,
        "route_status": route_status,
        "alias_matches": [item["operation"]["operation_code"] for item in matches],
        "source_request_digest": request_digest,
    }
    canonical_request = build_canonical_routed_request_v1(
        operation_code=operation_code,
        target_scope=target_scope,
        target_identifiers=normalize_identifier_list(
            [request.get("target"), request.get("query"), request.get("task")] + normalize_identifier_list(request.get("candidate_ids")),
            lowercase=False,
        ),
        constraints={
            "status_filter": request.get("status_filter", []),
            "requested_operation": operation_code,
        },
        authority_requirements=authority_requirements,
        freshness_requirements=freshness_requirements,
        output_contract=output_contract,
        presentation_preferences=presentation_preferences,
        candidate_policy_id=candidate_policy_id or operation_code,
        source_request_digest=request_digest,
        normalization_record=normalization_record,
    )
    normalization_record["canonical_request"] = canonical_request
    normalization_record["canonical_request_hash"] = hash_json_value(canonical_request)
    normalization_record["surface_request_digest"] = request_digest

    return {
        "route_status": route_status,
        "operation_code": operation_code,
        "handler_id": handler_id,
        "matched_rule_id": normalization_record.get("matched_rule_id"),
        "normalization_record": normalization_record,
        "ambiguity_record": ambiguity_record,
        "candidate_policy_id": candidate_policy_id or operation_code,
        "candidate_policy_version": selected.get("policy_version") if selected else None,
        "operation_registry": registry,
    }


def _safe_capsule_lookup(capsule: Mapping[str, Any] | None, *path: str) -> Any:
    current: Any = capsule or {}
    for key in path:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _safe_output_contract(request: Mapping[str, Any], selected: Mapping[str, Any], key: str) -> Any:
    if key in request and request.get(key) is not None:
        return request.get(key)
    allowed_output_contracts = list(selected.get("allowed_output_contracts", [])) if selected else []
    first_output_contract = allowed_output_contracts[0] if allowed_output_contracts else ""
    defaults = {
        "schema_id": normalize_text(first_output_contract),
        "schema_version": "1.0.0",
        "output_type": normalize_text(request.get("output_type") or request.get("requested_output_type") or selected.get("canonical_name"), lowercase=False),
    }
    return defaults.get(key)
