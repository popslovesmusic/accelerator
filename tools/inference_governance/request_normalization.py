from __future__ import annotations

import hashlib
import json
import posixpath
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


CANONICAL_ROUTED_REQUEST_SCHEMA_ID = "canonical_routed_request_v1"
CANONICAL_ROUTED_REQUEST_SCHEMA_VERSION = "1.0.0"
CANONICAL_ROUTED_REQUEST_HASH_FIELDS = (
    "operation_code",
    "target_scope",
    "target_identifiers",
    "constraints",
    "authority_requirements",
    "freshness_requirements",
    "output_contract",
    "candidate_policy_id",
)


def _stable_json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def hash_json_value(value: Any) -> str:
    digest = hashlib.sha256()
    digest.update(_stable_json_text(value).encode("utf-8"))
    return digest.hexdigest()


def normalize_text(value: Any, *, lowercase: bool = False, uppercase: bool = False) -> str:
    text = " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split()).strip()
    if lowercase:
        text = text.lower()
    if uppercase:
        text = text.upper()
    return text


def normalize_path_like(value: Any) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    text = text.replace("\\", "/")
    return posixpath.normpath(text)


def normalize_identifier(value: Any, *, lowercase: bool = False, uppercase: bool = False) -> str:
    return normalize_text(value, lowercase=lowercase, uppercase=uppercase)


def normalize_identifier_list(values: Any, *, lowercase: bool = False) -> list[str]:
    items: list[Any]
    if values is None:
        items = []
    elif isinstance(values, str):
        items = [values]
    elif isinstance(values, (list, tuple, set)):
        items = list(values)
    else:
        items = [values]

    normalized: list[str] = []
    for item in items:
        if isinstance(item, dict):
            candidate_id = item.get("candidate_id") or item.get("id") or item.get("name") or item.get("label")
        else:
            candidate_id = item
        text = normalize_identifier(candidate_id, lowercase=lowercase)
        if text and text not in normalized:
            normalized.append(text)
    return sorted(normalized)


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
        return normalize_text(value)
    return value


def normalize_constraints(constraints: Mapping[str, Any] | None) -> Dict[str, Any]:
    return dict(normalize_tree(dict(constraints or {})))


def _canonical_request_hash_basis(canonical_request: Mapping[str, Any]) -> Dict[str, Any]:
    request = dict(canonical_request or {})
    return {
        field: normalize_tree(request.get(field))
        for field in CANONICAL_ROUTED_REQUEST_HASH_FIELDS
    }


def hash_canonical_routed_request(canonical_request: Mapping[str, Any]) -> str:
    return hash_json_value(_canonical_request_hash_basis(canonical_request))


def build_canonical_routed_request_v1(
    *,
    operation_code: str,
    target_scope: Any,
    target_identifiers: Sequence[Any] | None,
    constraints: Mapping[str, Any] | None,
    authority_requirements: Mapping[str, Any] | None,
    freshness_requirements: Mapping[str, Any] | None,
    output_contract: Mapping[str, Any] | None,
    presentation_preferences: Mapping[str, Any] | None,
    candidate_policy_id: str,
    source_request_digest: str | None = None,
    normalization_record: Mapping[str, Any] | None = None,
    request_id: str | None = None,
    schema_id: str = CANONICAL_ROUTED_REQUEST_SCHEMA_ID,
    schema_version: str = CANONICAL_ROUTED_REQUEST_SCHEMA_VERSION,
) -> Dict[str, Any]:
    canonical_request = {
        "schema_id": normalize_identifier(schema_id),
        "schema_version": normalize_identifier(schema_version),
        "operation_code": normalize_identifier(operation_code, lowercase=True),
        "target_scope": normalize_tree(target_scope),
        "target_identifiers": normalize_identifier_list(target_identifiers or [], lowercase=False),
        "constraints": normalize_constraints(constraints),
        "authority_requirements": normalize_tree(dict(authority_requirements or {})),
        "freshness_requirements": normalize_tree(dict(freshness_requirements or {})),
        "output_contract": normalize_tree(dict(output_contract or {})),
        "presentation_preferences": normalize_tree(dict(presentation_preferences or {})),
        "candidate_policy_id": normalize_identifier(candidate_policy_id, lowercase=True),
        "source_request_digest": normalize_identifier(source_request_digest or ""),
        "normalization_record": normalize_tree(dict(normalization_record or {})),
    }

    canonical_request_id = request_id
    if not canonical_request_id:
        canonical_request_id = f"{canonical_request['schema_id']}:{hash_canonical_routed_request(canonical_request)[:16]}"
    canonical_request["request_id"] = normalize_identifier(canonical_request_id)
    return canonical_request


def canonical_request_surface_digest(surface_request: Mapping[str, Any]) -> str:
    return hash_json_value(normalize_tree(dict(surface_request or {})))
