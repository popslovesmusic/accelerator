from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

try:
    from scripts import query_governance as qg
except Exception:  # pragma: no cover - fallback only when scripts package is unavailable
    qg = None


CACHE_POLICY_VERSION = "decision_cache_policy_v1"
CACHE_NAMESPACE_DEFAULT = "governed_decision_cache_v1"
REQUEST_SEMANTICS_SCHEMA_ID = "request_semantics_v1"
DECISION_CACHE_KEY_SCHEMA_ID = "decision_cache_key_v1"
DECISION_CACHE_ENTRY_SCHEMA_ID = "decision_cache_entry_v1"
DECISION_CACHE_EVENT_SCHEMA_ID = "decision_cache_event_v1"
DECISION_CACHE_SCHEMA_VERSION = "1.0.0"
DEFAULT_BOUNDARY_POLICY_VERSION = "1.0.0"
DEFAULT_DETERMINISTIC_METHOD_VERSION = "1.0.0"
DEFAULT_VALIDATOR_ID = "decision_cache_validator_v1"
DEFAULT_VALIDATOR_VERSION = "1.0.0"
DEFAULT_OUTPUT_SCHEMA_VERSION = "1.0.0"
DEFAULT_RESULT_SCHEMA_ID = "semantic_readout_reply_v1"
CLASS_A_DETERMINISTIC_RESULT = "CLASS_A_DETERMINISTIC_RESULT"
CLASS_B_ACCEPTED_CONSTRAINED_OUTPUT = "CLASS_B_ACCEPTED_CONSTRAINED_OUTPUT"
CLASS_C_REJECTED_OR_FAILED_OUTPUT = "CLASS_C_REJECTED_OR_FAILED_OUTPUT"
CLASS_D_FORBIDDEN = "CLASS_D_FORBIDDEN"
SOURCE_DETERMINISTIC = "DETERMINISTIC"
SOURCE_ACCEPTED_CONSTRAINED_INFERENCE = "ACCEPTED_CONSTRAINED_INFERENCE"
SOURCE_NEGATIVE_RESULT = "NEGATIVE_RESULT"
REPLY_SOURCE_CACHED_DETERMINISTIC = "CACHED_DETERMINISTIC"
REPLY_SOURCE_CACHED_ACCEPTED_OUTPUT = "CACHED_ACCEPTED_OUTPUT"
CACHE_EVENT_TYPES = (
    "CACHE_LOOKUP",
    "CACHE_HIT",
    "CACHE_MISS",
    "CACHE_WRITE",
    "CACHE_WRITE_SKIPPED",
    "CACHE_INVALIDATED",
    "CACHE_CORRUPT",
    "CACHE_REVALIDATION_FAILED",
)

_SECRET_KEY_PATTERNS = (
    re.compile(r"authorization", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"bearer\s+[A-Za-z0-9._-]+", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
)


def _stable_json_text(value: Any) -> str:
    if qg is not None and hasattr(qg, "_canonical_json_text"):
        try:
            return str(qg._canonical_json_text(value))
        except Exception:
            pass
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def hash_json_value(value: Any) -> str:
    if qg is not None and hasattr(qg, "_hash_json_value"):
        try:
            return str(qg._hash_json_value(value))
        except Exception:
            pass
    digest = hashlib.sha256()
    digest.update(_stable_json_text(value).encode("utf-8"))
    return digest.hexdigest()


def normalize_string(value: Any, *, lowercase: bool = False, uppercase: bool = False) -> str:
    text = " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split()).strip()
    if lowercase:
        text = text.lower()
    if uppercase:
        text = text.upper()
    return text


def normalize_identifier_list(values: Any) -> list[str]:
    items: list[str] = []
    if isinstance(values, str):
        values = [values]
    if isinstance(values, (list, tuple, set)):
        for value in values:
            text = normalize_string(value)
            if text and text not in items:
                items.append(text)
    return sorted(items)


def normalize_path_like(value: Any) -> str:
    text = normalize_string(value)
    return text.replace("\\", "/")


def normalize_tree(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): normalize_tree(value[key]) for key in sorted(value.keys(), key=lambda item: str(item))}
    if isinstance(value, list):
        return [normalize_tree(item) for item in value]
    if isinstance(value, tuple):
        return [normalize_tree(item) for item in value]
    if isinstance(value, set):
        normalized = [normalize_tree(item) for item in value]
        return sorted(normalized, key=_stable_json_text)
    if isinstance(value, str):
        return normalize_string(value)
    return value


def normalize_request_semantics(request_semantics: Mapping[str, Any]) -> Dict[str, Any]:
    semantics = dict(request_semantics or {})
    normalized: Dict[str, Any] = {
        "operation": normalize_string(semantics.get("operation")),
        "target_scope": normalize_tree(semantics.get("target_scope")),
        "requested_output_type": normalize_string(semantics.get("requested_output_type")),
        "constraints": normalize_tree(semantics.get("constraints") or {}),
        "candidate_ids": normalize_identifier_list(semantics.get("candidate_ids")),
        "exclusions": normalize_identifier_list(semantics.get("exclusions")),
    }
    diagnostic_metadata = semantics.get("diagnostic_metadata")
    if diagnostic_metadata is not None:
        normalized["diagnostic_metadata"] = normalize_tree(diagnostic_metadata)
    for optional in ("authority_class", "boundary_id", "purpose_code", "cache_namespace", "decision_type"):
        if optional in semantics and semantics[optional] is not None:
            normalized[optional] = normalize_string(semantics[optional], lowercase=False)
    return normalized


def build_request_semantics_v1(
    *,
    operation: str,
    target_scope: Any,
    requested_output_type: str,
    constraints: Mapping[str, Any],
    candidate_ids: Sequence[Any] | None,
    exclusions: Sequence[Any] | None,
    diagnostic_metadata: Mapping[str, Any] | None = None,
    boundary_id: str | None = None,
    purpose_code: str | None = None,
    authority_class: str | None = None,
    cache_namespace: str | None = None,
    decision_type: str | None = None,
) -> Dict[str, Any]:
    request_semantics = {
        "schema_id": REQUEST_SEMANTICS_SCHEMA_ID,
        "schema_version": DECISION_CACHE_SCHEMA_VERSION,
        "operation": normalize_string(operation, lowercase=True),
        "target_scope": normalize_tree(target_scope),
        "requested_output_type": normalize_string(requested_output_type),
        "constraints": normalize_tree(dict(constraints or {})),
        "candidate_ids": normalize_identifier_list(candidate_ids or ()),
        "exclusions": normalize_identifier_list(exclusions or ()),
    }
    if diagnostic_metadata:
        request_semantics["diagnostic_metadata"] = normalize_tree(dict(diagnostic_metadata))
    if boundary_id:
        request_semantics["boundary_id"] = normalize_string(boundary_id)
    if purpose_code:
        request_semantics["purpose_code"] = normalize_string(purpose_code)
    if authority_class:
        request_semantics["authority_class"] = normalize_string(authority_class, uppercase=True)
    if cache_namespace:
        request_semantics["cache_namespace"] = normalize_string(cache_namespace)
    if decision_type:
        request_semantics["decision_type"] = normalize_string(decision_type)
    return request_semantics


def classify_semantic_readout_result(result: Mapping[str, Any]) -> Dict[str, Any]:
    payload = dict(result or {})
    schema_id = normalize_string(payload.get("schema_id"))
    schema_version = normalize_string(payload.get("schema_version"))
    reply_source = normalize_string(payload.get("reply_source"), uppercase=True)
    backend_status = normalize_string(payload.get("backend_status"), uppercase=True)
    fallback_used = bool(payload.get("fallback_used", False))
    cache_hit = bool(payload.get("cache_hit", False))

    if not isinstance(payload, dict) or not schema_id or not schema_version:
        return {
            "cacheable": False,
            "cache_class": CLASS_D_FORBIDDEN,
            "source": SOURCE_NEGATIVE_RESULT,
            "stored_reply_source": None,
            "reason_code": "RESULT_SCHEMA_INVALID",
        }

    if _contains_forbidden_content(payload):
        return {
            "cacheable": False,
            "cache_class": CLASS_D_FORBIDDEN,
            "source": SOURCE_NEGATIVE_RESULT,
            "stored_reply_source": None,
            "reason_code": "FORBIDDEN_CONTENT",
        }

    if cache_hit or reply_source in {REPLY_SOURCE_CACHED_DETERMINISTIC, REPLY_SOURCE_CACHED_ACCEPTED_OUTPUT}:
        return {
            "cacheable": False,
            "cache_class": CLASS_D_FORBIDDEN,
            "source": SOURCE_NEGATIVE_RESULT,
            "stored_reply_source": None,
            "reason_code": "ALREADY_CACHED",
        }

    if reply_source == "LOCAL_DETERMINISTIC" and backend_status in {"NOT_REQUESTED", "DENIED"}:
        return {
            "cacheable": True,
            "cache_class": CLASS_A_DETERMINISTIC_RESULT,
            "source": SOURCE_DETERMINISTIC,
            "stored_reply_source": REPLY_SOURCE_CACHED_DETERMINISTIC,
            "reason_code": "DETERMINISTIC_RESULT",
        }

    if reply_source == "NETWORK_MODEL" and backend_status == "SUCCESS" and not fallback_used:
        return {
            "cacheable": True,
            "cache_class": CLASS_B_ACCEPTED_CONSTRAINED_OUTPUT,
            "source": SOURCE_ACCEPTED_CONSTRAINED_INFERENCE,
            "stored_reply_source": REPLY_SOURCE_CACHED_ACCEPTED_OUTPUT,
            "reason_code": "ACCEPTED_CONSTRAINED_OUTPUT",
        }

    if backend_status == "FAILED":
        return {
            "cacheable": False,
            "cache_class": CLASS_C_REJECTED_OR_FAILED_OUTPUT,
            "source": SOURCE_NEGATIVE_RESULT,
            "stored_reply_source": None,
            "reason_code": "UNSTABLE_FAILURE_STATE",
        }

    return {
        "cacheable": False,
        "cache_class": CLASS_D_FORBIDDEN,
        "source": SOURCE_NEGATIVE_RESULT,
        "stored_reply_source": None,
        "reason_code": "UNSUPPORTED_RESULT_SOURCE",
    }


def build_cached_result_payload(
    result: Mapping[str, Any],
    *,
    cache_key: str,
    cache_class: str,
    cache_namespace: str,
    stored_reply_source: str,
    cache_hit: bool = True,
) -> Dict[str, Any]:
    payload = dict(result or {})
    payload["reply_source"] = stored_reply_source
    payload["cache_hit"] = bool(cache_hit)
    payload["cache_key"] = cache_key
    payload["cache_class"] = cache_class
    payload["cache_namespace"] = cache_namespace
    return payload


def build_validation_record(
    *,
    validated_at: str,
    validator_id: str = DEFAULT_VALIDATOR_ID,
    validator_version: str = DEFAULT_VALIDATOR_VERSION,
    schema_id: str = DEFAULT_RESULT_SCHEMA_ID,
    schema_version: str = DECISION_CACHE_SCHEMA_VERSION,
) -> Dict[str, Any]:
    return {
        "status": "accepted",
        "schema_id": schema_id,
        "schema_version": schema_version,
        "validator_id": validator_id,
        "validator_version": validator_version,
        "validated_at": validated_at,
    }


def build_provenance_record(
    *,
    request_semantics_hash: str,
    capsule_hash: str,
    boundary_id: str,
    purpose_code: str,
    policy_version: str,
    candidate_set_hash: str,
    authority_hash: str,
    freshness_hash: str,
    cache_namespace: str,
    decision_type: str,
) -> Dict[str, Any]:
    return {
        "request_semantics_hash": request_semantics_hash,
        "capsule_hash": capsule_hash,
        "boundary_id": boundary_id,
        "purpose_code": purpose_code,
        "policy_version": policy_version,
        "candidate_set_hash": candidate_set_hash,
        "authority_hash": authority_hash,
        "freshness_hash": freshness_hash,
        "cache_namespace": cache_namespace,
        "decision_type": decision_type,
    }


def build_invalidation_dependency_record(
    *,
    capsule_hash: str,
    authority_hash: str,
    freshness_hash: str,
    boundary_id: str,
    boundary_policy_version: str,
    deterministic_method_version: str,
    validator_version: str,
    output_schema_version: str,
    candidate_set_hash: str,
    request_semantics_hash: str,
    tool_registry_hash: str | None = None,
    repository_snapshot_hash: str | None = None,
    runtime_signature_hash: str | None = None,
    configuration_hash: str | None = None,
) -> Dict[str, Any]:
    return {
        "capsule_hash": capsule_hash,
        "authority_hash": authority_hash,
        "freshness_hash": freshness_hash,
        "boundary_id": boundary_id,
        "boundary_policy_version": boundary_policy_version,
        "deterministic_method_version": deterministic_method_version,
        "validator_version": validator_version,
        "output_schema_version": output_schema_version,
        "candidate_set_hash": candidate_set_hash,
        "request_semantics_hash": request_semantics_hash,
        "tool_registry_hash": tool_registry_hash,
        "repository_snapshot_hash": repository_snapshot_hash,
        "runtime_signature_hash": runtime_signature_hash,
        "configuration_hash": configuration_hash,
    }


def build_cache_key_payload(
    *,
    cache_namespace: str,
    decision_type: str,
    request_semantics_hash: str,
    capsule_hash: str,
    authority_hash: str,
    freshness_hash: str,
    boundary_id: str,
    boundary_policy_version: str,
    purpose_code: str,
    caller_policy_class: str,
    candidate_set_hash: str,
    deterministic_method_version: str,
    validator_version: str,
    output_schema_version: str,
    tool_registry_hash: str | None = None,
    repository_snapshot_hash: str | None = None,
    runtime_signature_hash: str | None = None,
    configuration_hash: str | None = None,
) -> Dict[str, Any]:
    payload = {
        "cache_namespace": normalize_string(cache_namespace),
        "decision_type": normalize_string(decision_type),
        "request_semantics_hash": normalize_string(request_semantics_hash),
        "capsule_hash": normalize_string(capsule_hash),
        "authority_hash": normalize_string(authority_hash),
        "freshness_hash": normalize_string(freshness_hash),
        "boundary_id": normalize_string(boundary_id),
        "boundary_policy_version": normalize_string(boundary_policy_version),
        "purpose_code": normalize_string(purpose_code),
        "caller_policy_class": normalize_string(caller_policy_class),
        "candidate_set_hash": normalize_string(candidate_set_hash),
        "deterministic_method_version": normalize_string(deterministic_method_version),
        "validator_version": normalize_string(validator_version),
        "output_schema_version": normalize_string(output_schema_version),
        "tool_registry_hash": normalize_string(tool_registry_hash) if tool_registry_hash else None,
        "repository_snapshot_hash": normalize_string(repository_snapshot_hash) if repository_snapshot_hash else None,
        "runtime_signature_hash": normalize_string(runtime_signature_hash) if runtime_signature_hash else None,
        "configuration_hash": normalize_string(configuration_hash) if configuration_hash else None,
    }
    return payload


def hash_request_semantics(request_semantics: Mapping[str, Any]) -> str:
    return hash_json_value(normalize_request_semantics(request_semantics))


def hash_cache_key_payload(cache_key_payload: Mapping[str, Any]) -> str:
    return hash_json_value(dict(cache_key_payload or {}))


def _contains_forbidden_content(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = normalize_string(key, lowercase=True)
            if key_text in {
                "authorization",
                "authorization_header",
                "proxy-authorization",
                "api_key",
                "access_token",
                "refresh_token",
                "id_token",
                "secret",
                "token",
            }:
                return True
            if _contains_forbidden_content(item):
                return True
        return False
    if isinstance(value, (list, tuple, set)):
        return any(_contains_forbidden_content(item) for item in value)
    if isinstance(value, str):
        text = value.strip()
        if "Bearer " in text:
            return True
        if any(pattern.search(text) for pattern in _SECRET_KEY_PATTERNS):
            return True
    return False


def validate_semantic_readout_reply_payload(payload: Mapping[str, Any]) -> list[str]:
    result = dict(payload or {})
    errors: list[str] = []
    required = (
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
    )
    for field in required:
        if field not in result:
            errors.append(f"missing_field:{field}")

    schema_id = normalize_string(result.get("schema_id"))
    schema_version = normalize_string(result.get("schema_version"))
    if schema_id and schema_id != DEFAULT_RESULT_SCHEMA_ID:
        errors.append("schema_id_mismatch")
    if schema_version and schema_version != DECISION_CACHE_SCHEMA_VERSION:
        errors.append("schema_version_mismatch")

    reply_source = normalize_string(result.get("reply_source"), uppercase=True)
    allowed_sources = {
        "LOCAL_DETERMINISTIC",
        "NETWORK_MODEL",
        REPLY_SOURCE_CACHED_DETERMINISTIC,
        REPLY_SOURCE_CACHED_ACCEPTED_OUTPUT,
    }
    if reply_source and reply_source not in allowed_sources:
        errors.append("reply_source_invalid")

    backend_status = normalize_string(result.get("backend_status"), uppercase=True)
    allowed_statuses = {"NOT_REQUESTED", "DENIED", "SUCCESS", "FAILED"}
    if backend_status and backend_status not in allowed_statuses:
        errors.append("backend_status_invalid")

    if _contains_forbidden_content(result):
        errors.append("forbidden_content")
    return errors


def build_cache_key_materialized_record(
    *,
    cache_namespace: str,
    decision_type: str,
    request_semantics: Mapping[str, Any],
    capsule_hash: str,
    authority_hash: str,
    freshness_hash: str,
    boundary_id: str,
    boundary_policy_version: str,
    purpose_code: str,
    caller_policy_class: str,
    candidate_set_hash: str,
    deterministic_method_version: str,
    validator_version: str,
    output_schema_version: str,
    tool_registry_hash: str | None = None,
    repository_snapshot_hash: str | None = None,
    runtime_signature_hash: str | None = None,
    configuration_hash: str | None = None,
) -> Dict[str, Any]:
    request_semantics_normalized = normalize_request_semantics(request_semantics)
    request_semantics_hash = hash_request_semantics(request_semantics_normalized)
    cache_key_payload = build_cache_key_payload(
        cache_namespace=cache_namespace,
        decision_type=decision_type,
        request_semantics_hash=request_semantics_hash,
        capsule_hash=capsule_hash,
        authority_hash=authority_hash,
        freshness_hash=freshness_hash,
        boundary_id=boundary_id,
        boundary_policy_version=boundary_policy_version,
        purpose_code=purpose_code,
        caller_policy_class=caller_policy_class,
        candidate_set_hash=candidate_set_hash,
        deterministic_method_version=deterministic_method_version,
        validator_version=validator_version,
        output_schema_version=output_schema_version,
        tool_registry_hash=tool_registry_hash,
        repository_snapshot_hash=repository_snapshot_hash,
        runtime_signature_hash=runtime_signature_hash,
        configuration_hash=configuration_hash,
    )
    return {
        "cache_key_schema_id": DECISION_CACHE_KEY_SCHEMA_ID,
        "cache_key_schema_version": DECISION_CACHE_SCHEMA_VERSION,
        "request_semantics": request_semantics_normalized,
        "request_semantics_hash": request_semantics_hash,
        "cache_key_payload": cache_key_payload,
        "cache_key": hash_cache_key_payload(cache_key_payload),
    }
