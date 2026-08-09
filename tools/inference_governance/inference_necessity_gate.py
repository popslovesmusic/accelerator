from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional, Sequence, Tuple

try:
    from scripts import query_governance as qg
except Exception:  # pragma: no cover - fallback only when scripts package is unavailable
    qg = None


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INFERENCE_BOUNDARY_REGISTRY_PATH = ROOT / "registry" / "inference_boundary_registry.json"
DEFAULT_INFERENCE_GATE_EVENT_SCHEMA_ID = "inference_gate_event_v1"
DEFAULT_INFERENCE_GATE_SCHEMA_VERSION = "1.0.0"
DEFAULT_INFERENCE_BOUNDARY_REGISTRY_SCHEMA_ID = "inference_boundary_registry_v1"
DEFAULT_INFERENCE_BOUNDARY_REGISTRY_SCHEMA_VERSION = "1.0.0"
DEFAULT_ALLOWED_MODES: Tuple[str, ...] = ("CONSTRAINED",)
DEFAULT_BUDGET = {
    "maximum_calls": 0,
    "maximum_retries": 0,
    "maximum_input_tokens": 0,
    "maximum_output_tokens": 0,
    "maximum_latency_ms": 0,
}
MATERIALITY_RANK = {
    "NONE": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}
EXECUTABLE_BOUNDARY_PATTERNS = (
    re.compile(r"urllib\.request\.urlopen"),
    re.compile(r"/v1/chat/completions"),
    re.compile(r"openai_compatible"),
    re.compile(r"SEMANTIC_READOUT_API_KEY"),
    re.compile(r"OPENAI_API_KEY"),
)
CONFIG_ACTIVATION_PATTERNS = (
    re.compile(r"enable_network_semantic_readout"),
    re.compile(r"allowed_network_endpoints"),
    re.compile(r"network_retry_budget"),
    re.compile(r"retry_budget"),
    re.compile(r"openai_compatible"),
)


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _first(mapping: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return default


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def _hash_json_value(value: Any) -> str:
    if qg is not None and hasattr(qg, "_hash_json_value"):
        try:
            return str(qg._hash_json_value(value))
        except Exception:
            pass
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _approx_token_count(value: Any) -> int:
    text = value if isinstance(value, str) else _stable_json(value)
    if not text:
        return 0
    try:
        return max(1, (len(text.encode("utf-8")) + 3) // 4)
    except Exception:
        return 0


def _normalize_string_list(value: Any, default: Tuple[str, ...] = ()) -> Tuple[str, ...]:
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        items = []
    normalized = []
    for item in items:
        text = str(item or "").strip()
        if text and text not in normalized:
            normalized.append(text)
    return tuple(normalized) if normalized else tuple(default)


def _normalize_candidate_set(candidate_set: Any) -> Tuple[str, ...]:
    if candidate_set is None:
        return ()
    items: list[Any]
    if isinstance(candidate_set, dict):
        if "candidate_ids" in candidate_set:
            items = list(candidate_set.get("candidate_ids") or [])
        elif "candidates" in candidate_set:
            items = list(candidate_set.get("candidates") or [])
        else:
            items = list(candidate_set.values())
    elif isinstance(candidate_set, (list, tuple, set)):
        items = list(candidate_set)
    else:
        items = [candidate_set]

    normalized: list[str] = []
    for item in items:
        if isinstance(item, dict):
            candidate_id = item.get("candidate_id") or item.get("id") or item.get("name") or item.get("label")
            if candidate_id is None:
                candidate_id = _stable_json(item)
        else:
            candidate_id = item
        text = str(candidate_id or "").strip()
        if text and text not in normalized:
            normalized.append(text)
    return tuple(normalized)


def _normalize_budget(value: Any) -> Dict[str, int]:
    source = _as_dict(value)
    normalized = {}
    for key in DEFAULT_BUDGET:
        try:
            normalized[key] = max(0, int(_first(source, key, default=0) or 0))
        except Exception:
            normalized[key] = 0
    return normalized


def _merge_budget(ceiling: Dict[str, int], request: Dict[str, int]) -> Dict[str, int]:
    normalized_ceiling = _normalize_budget(ceiling)
    normalized_request = _normalize_budget(request)
    return {
        key: min(normalized_ceiling.get(key, 0), normalized_request.get(key, 0))
        for key in DEFAULT_BUDGET
    }


def _materiality_rank(value: Any) -> int:
    text = str(value or "").strip().upper()
    return MATERIALITY_RANK.get(text, 0)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def load_inference_boundary_registry(path: Optional[str | Path] = None) -> Dict[str, Any]:
    registry_path = Path(path) if path is not None else DEFAULT_INFERENCE_BOUNDARY_REGISTRY_PATH
    if not registry_path.exists():
        return {
            "schema_id": DEFAULT_INFERENCE_BOUNDARY_REGISTRY_SCHEMA_ID,
            "schema_version": DEFAULT_INFERENCE_BOUNDARY_REGISTRY_SCHEMA_VERSION,
            "generated_at": None,
            "boundaries": [],
            "false_positives": [],
        }
    return _load_json(registry_path)


def validate_inference_boundary_registry_payload(registry: Any) -> list[str]:
    registry_dict = _as_dict(registry)
    errors: list[str] = []
    if not registry_dict:
        return ["registry_missing"]
    if registry_dict.get("schema_id") != DEFAULT_INFERENCE_BOUNDARY_REGISTRY_SCHEMA_ID:
        errors.append("schema_id_mismatch")
    if registry_dict.get("schema_version") != DEFAULT_INFERENCE_BOUNDARY_REGISTRY_SCHEMA_VERSION:
        errors.append("schema_version_mismatch")
    boundaries = registry_dict.get("boundaries")
    if not isinstance(boundaries, list):
        errors.append("boundaries_not_array")
        boundaries = []
    for index, entry in enumerate(boundaries):
        if not isinstance(entry, dict):
            errors.append(f"boundary_entry_not_object:{index}")
            continue
        for field in (
            "boundary_id",
            "path",
            "symbol",
            "status",
            "owner",
            "allowed_callers",
            "allowed_purposes",
            "allowed_modes",
            "default_budget",
            "budget_ceiling",
            "deterministic_fallback",
            "output_schema",
            "telemetry_schema",
            "retry_policy",
            "authority_class",
            "last_audited",
        ):
            if field not in entry:
                errors.append(f"missing_boundary_field:{field}")
        if not isinstance(entry.get("default_budget"), dict):
            errors.append(f"default_budget_not_object:{entry.get('boundary_id')}")
        if not isinstance(entry.get("budget_ceiling"), dict):
            errors.append(f"budget_ceiling_not_object:{entry.get('boundary_id')}")
    return errors


def _load_boundary_entry(boundary_id: str, registry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    boundary_text = str(boundary_id or "").strip()
    for entry in registry.get("boundaries", []) if isinstance(registry.get("boundaries"), list) else []:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("boundary_id", "")).strip() == boundary_text:
            return entry
    return None


def _merge_boundary_policy(registry_entry: Dict[str, Any], boundary_policy: Any) -> Dict[str, Any]:
    overlay = _as_dict(boundary_policy)
    merged = dict(registry_entry or {})
    for field in (
        "allowed_callers",
        "allowed_purposes",
        "allowed_modes",
        "default_budget",
        "budget_ceiling",
        "authority_class",
        "status",
        "retry_policy",
        "candidate_generation_must_be_deterministic",
        "candidate_count_required",
        "open_mode_enabled",
        "deterministic_fallback",
    ):
        if field in overlay and overlay[field] is not None:
            merged[field] = overlay[field]
    return merged


def _capsule_hash_basis(capsule: Dict[str, Any]) -> Dict[str, Any]:
    capsule_dict = _as_dict(capsule)
    provenance = _as_dict(_first(capsule_dict, "provenance", default={}))
    return {
        "schema_id": str(_first(capsule_dict, "schema_id", default="")),
        "schema_version": str(_first(capsule_dict, "schema_version", default="")),
        "capsule_schema_version": str(_first(capsule_dict, "capsule_schema_version", default="")),
        "request_identity": _as_dict(_first(capsule_dict, "request_identity", default={})),
        "section_hashes": _as_dict(_first(provenance, "section_hashes", default={})),
        "source_fingerprint": {
            "db_path": provenance.get("db_path"),
            "target": provenance.get("target"),
            "task": provenance.get("task"),
            "query": provenance.get("query"),
            "focus_query": provenance.get("focus_query"),
            "schema_version": provenance.get("schema_version"),
            "producer": provenance.get("producer"),
            "producer_version": provenance.get("producer_version"),
            "source_paths": provenance.get("source_paths"),
            "source_hashes": provenance.get("source_hashes"),
            "source_count": provenance.get("source_count"),
            "excluded_source_count": provenance.get("excluded_source_count"),
        },
        "summary": _as_dict(_first(capsule_dict, "summary", default={})),
    }


def _capsule_hash(capsule: Any) -> str:
    capsule_dict = _as_dict(capsule)
    direct = str(_first(capsule_dict, "capsule_hash", default="")).strip()
    if direct:
        return direct
    try:
        return _hash_json_value(_capsule_hash_basis(capsule_dict))
    except Exception:
        return ""


def _governed_context_capsule_validation(capsule: Any) -> Tuple[bool, str, str, list[str]]:
    capsule_dict = _as_dict(capsule)
    if not capsule_dict:
        return False, "CAPSULE_MISSING", "", ["missing_governed_context_capsule"]

    expected_hash = _capsule_hash(capsule_dict)
    expected_id = f"{str(_first(capsule_dict, 'schema_id', default=DEFAULT_INFERENCE_BOUNDARY_REGISTRY_SCHEMA_ID)).strip() or DEFAULT_INFERENCE_BOUNDARY_REGISTRY_SCHEMA_ID}:{expected_hash[:16]}"

    if qg is not None and hasattr(qg, "validate_governed_context_capsule_payload"):
        try:
            errors = list(
                qg.validate_governed_context_capsule_payload(
                    capsule_dict,
                    expected_hash=expected_hash or None,
                    expected_id=expected_id or None,
                )
            )
        except Exception as exc:  # pragma: no cover - defensive fallback
            return False, "CAPSULE_INVALID", expected_hash, [f"validation_exception:{exc.__class__.__name__}"]
        if errors:
            if "capsule_hash_mismatch" in errors:
                return False, "CAPSULE_HASH_INVALID", expected_hash, errors
            return False, "CAPSULE_INVALID", expected_hash, errors
        return True, "CAPSULE_VALID", expected_hash, []

    errors: list[str] = []
    required = (
        "schema_id",
        "schema_version",
        "capsule_id",
        "capsule_hash",
        "request_identity",
        "current_state",
        "freshness",
        "authority",
        "patch_chain",
        "open_debt",
        "relevant_artifacts",
        "runtime_trace",
        "candidate_actions",
        "exclusions",
        "provenance",
        "metrics",
    )
    for field in required:
        if field not in capsule_dict:
            errors.append(f"missing_top_level_field:{field}")
    if expected_hash and str(_first(capsule_dict, "capsule_hash", default="")).strip() != expected_hash:
        errors.append("capsule_hash_mismatch")
    if expected_id and str(_first(capsule_dict, "capsule_id", default="")).strip() != expected_id:
        errors.append("capsule_id_mismatch")
    if errors:
        if "capsule_hash_mismatch" in errors:
            return False, "CAPSULE_HASH_INVALID", expected_hash, errors
        return False, "CAPSULE_INVALID", expected_hash, errors
    return True, "CAPSULE_VALID", expected_hash, []


def _normalize_deterministic_attempt_record(record: Any) -> Dict[str, Any]:
    source = _as_dict(record)
    methods_considered = _normalize_string_list(source.get("methods_considered"))
    methods_executed = _normalize_string_list(source.get("methods_executed"))
    results = source.get("results") if isinstance(source.get("results"), dict) else {}
    explanation = str(_first(source, "explanation", "reason", default="")).strip()
    normalized = {
        "methods_considered": list(methods_considered),
        "methods_executed": list(methods_executed),
        "results": dict(results),
        "deterministic_answer_available": bool(_first(source, "deterministic_answer_available", default=False)),
        "cache_answer_available": bool(_first(source, "cache_answer_available", default=False)),
        "machine_readable_resolution_available": bool(_first(source, "machine_readable_resolution_available", default=False)),
        "finite_candidate_resolution_available": bool(_first(source, "finite_candidate_resolution_available", default=False)),
        "failure_signature_resolution_available": bool(_first(source, "failure_signature_resolution_available", default=False)),
        "explanation": explanation,
    }
    normalized["is_well_formed"] = bool(normalized["methods_considered"]) and bool(normalized["explanation"])
    return normalized


def _normalize_uncertainty_record(record: Any) -> Dict[str, Any]:
    source = _as_dict(record)
    materiality = str(_first(source, "materiality", default="NONE")).strip().upper() or "NONE"
    resolution_need = str(_first(source, "resolution_need", default="OPTIONAL_PRESENTATION")).strip().upper() or "OPTIONAL_PRESENTATION"
    normalized = {
        "uncertainty_id": str(_first(source, "uncertainty_id", default="")).strip(),
        "description": str(_first(source, "description", default="")).strip(),
        "materiality": materiality if materiality in MATERIALITY_RANK else "NONE",
        "resolution_need": resolution_need,
        "known_bounds": source.get("known_bounds"),
        "unresolved_dimensions": list(_normalize_string_list(source.get("unresolved_dimensions"))),
        "consequence_of_no_inference": str(_first(source, "consequence_of_no_inference", default="")).strip(),
    }
    normalized["is_well_formed"] = bool(normalized["description"]) and bool(normalized["consequence_of_no_inference"])
    return normalized


def _normalize_budget_ceiling(policy: Dict[str, Any]) -> Dict[str, int]:
    return _normalize_budget(_first(policy, "budget_ceiling", "maximum_budget", "default_budget", default=DEFAULT_BUDGET))


def _build_gate_event(
    *,
    event_type: str,
    decision: str,
    reason_code: str,
    boundary_id: str,
    caller_id: str,
    purpose_code: str,
    request_id: str,
    capsule_hash: str,
    deterministic_methods_considered: Sequence[str],
    deterministic_methods_executed: Sequence[str],
    remaining_uncertainty: Dict[str, Any],
    candidate_count: int,
    effective_budget: Dict[str, int],
    actual_calls: int,
    actual_input_tokens: Optional[int],
    actual_output_tokens: Optional[int],
    latency_ms: Optional[float],
    fallback_used: bool,
    error_class: Optional[str],
) -> Dict[str, Any]:
    return {
        "event_type": event_type,
        "event_id": uuid.uuid4().hex,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "boundary_id": boundary_id,
        "caller_id": caller_id,
        "purpose_code": purpose_code,
        "request_id": request_id,
        "capsule_hash": capsule_hash,
        "decision": decision,
        "reason_code": reason_code,
        "authorized_mode": "CONSTRAINED" if decision == "AUTHORIZE_CONSTRAINED_INFERENCE" else ("OPEN" if decision == "AUTHORIZE_OPEN_INFERENCE" else "NONE"),
        "deterministic_methods_considered": list(deterministic_methods_considered),
        "deterministic_methods_executed": list(deterministic_methods_executed),
        "remaining_uncertainty": remaining_uncertainty,
        "candidate_count": int(candidate_count),
        "effective_budget": effective_budget,
        "actual_calls": int(actual_calls),
        "actual_input_tokens": actual_input_tokens,
        "actual_output_tokens": actual_output_tokens,
        "latency_ms": latency_ms,
        "fallback_used": bool(fallback_used),
        "error_class": error_class,
    }


def _emit_gate_event(event: Dict[str, Any], telemetry_sink: Optional[Callable[[Dict[str, Any]], None]] = None) -> str:
    try:
        LOGGER.info("%s", _stable_json(event))
    except Exception:
        pass
    if telemetry_sink is not None:
        try:
            telemetry_sink(dict(event))
        except Exception:
            pass
    return str(event.get("event_id") or "")


def _resolve_call_or_purpose_allowed(values: Tuple[str, ...], request_value: str) -> bool:
    if not values:
        return False
    return request_value in values


def _boundary_status_allows_inference(status: str) -> bool:
    return str(status or "").strip().upper() in {"ACTIVE", "LATENT", "TEST_ONLY"}


def _evaluate_budget(request_budget: Dict[str, int], ceiling_budget: Dict[str, int]) -> Tuple[bool, str]:
    if not any(request_budget.values()):
        return False, "DENY_BUDGET_EXHAUSTED"
    for key in DEFAULT_BUDGET:
        if request_budget.get(key, 0) <= 0:
            return False, "DENY_BUDGET_EXHAUSTED"
        if ceiling_budget.get(key, 0) > 0 and request_budget.get(key, 0) > ceiling_budget.get(key, 0):
            return False, "DENY_BUDGET_EXHAUSTED"
    return True, "AUTHORIZE_CONSTRAINED_INFERENCE"


def evaluate_inference_necessity_gate(
    *,
    boundary_id: str,
    caller_id: Optional[str],
    purpose_code: Optional[str],
    request_id: Optional[str],
    governed_context_capsule: Optional[Dict[str, Any]],
    deterministic_attempt_record: Optional[Dict[str, Any]],
    uncertainty_record: Optional[Dict[str, Any]],
    candidate_set: Optional[Iterable[Any]],
    inference_budget: Optional[Dict[str, Any]],
    boundary_policy: Optional[Dict[str, Any]] = None,
    decision_cache_store: Optional[Any] = None,
    cache_request: Optional[Dict[str, Any]] = None,
    telemetry_sink: Optional[Callable[[Dict[str, Any]], None]] = None,
    registry_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    started_at = time.perf_counter()
    boundary_text = str(boundary_id or "").strip()
    caller_text = str(caller_id or "").strip()
    purpose_text = str(purpose_code or "").strip()
    request_text = str(request_id or "").strip()
    registry = load_inference_boundary_registry(registry_path)
    registry_errors = validate_inference_boundary_registry_payload(registry)
    boundary_entry = _load_boundary_entry(boundary_text, registry)
    merged_policy = _merge_boundary_policy(boundary_entry or {}, boundary_policy)
    capsule_dict = _as_dict(governed_context_capsule)
    candidate_values = _normalize_candidate_set(candidate_set)
    attempt = _normalize_deterministic_attempt_record(deterministic_attempt_record)
    uncertainty = _normalize_uncertainty_record(uncertainty_record)
    request_budget = _normalize_budget(inference_budget)
    budget_ceiling = _normalize_budget_ceiling(merged_policy)
    capsule_valid, capsule_reason, capsule_hash, capsule_errors = _governed_context_capsule_validation(capsule_dict)
    deterministic_methods_attempted = list(attempt["methods_considered"])
    deterministic_methods_executed = list(attempt["methods_executed"])
    remaining_uncertainty = dict(uncertainty)
    candidate_count = len(candidate_values)
    effective_budget = _merge_budget(budget_ceiling, request_budget)
    cache_lookup_result = None
    cache_lookup_payload = None
    cached_result = None

    if decision_cache_store is not None and cache_request is not None:
        try:
            cache_lookup_result = decision_cache_store.lookup(cache_request)
        except Exception:
            cache_lookup_result = None
        if cache_lookup_result is not None:
            cache_lookup_payload = cache_lookup_result.as_dict()
            if cache_lookup_result.hit:
                attempt["cache_answer_available"] = True
                attempt_results = dict(attempt.get("results") or {})
                cache_attempt_result = dict(attempt_results.get("CACHE") or {})
                cache_attempt_result["cache_answer_available"] = True
                cache_attempt_result["cache_scope"] = "decision_cache"
                attempt_results["CACHE"] = cache_attempt_result
                attempt["results"] = attempt_results
                cached_result = dict(cache_lookup_result.result or {})
                decision = "DENY_CACHE_RESULT_AVAILABLE"
                reason_code = "CACHE_RESULT_AVAILABLE"
                authorized = False
                authorized_mode = "NONE"

                evaluation_event = _build_gate_event(
                    event_type="GATE_EVALUATED",
                    decision=decision,
                    reason_code=reason_code,
                    boundary_id=boundary_text,
                    caller_id=caller_text,
                    purpose_code=purpose_text,
                    request_id=request_text,
                    capsule_hash=capsule_hash,
                    deterministic_methods_considered=deterministic_methods_attempted,
                    deterministic_methods_executed=deterministic_methods_executed,
                    remaining_uncertainty=remaining_uncertainty,
                    candidate_count=candidate_count,
                    effective_budget=effective_budget,
                    actual_calls=0,
                    actual_input_tokens=None,
                    actual_output_tokens=None,
                    latency_ms=(time.perf_counter() - started_at) * 1000.0,
                    fallback_used=False,
                    error_class=None,
                )
                evaluation_event_id = _emit_gate_event(evaluation_event, telemetry_sink=telemetry_sink)

                decision_event = _build_gate_event(
                    event_type="GATE_DENIED",
                    decision=decision,
                    reason_code=reason_code,
                    boundary_id=boundary_text,
                    caller_id=caller_text,
                    purpose_code=purpose_text,
                    request_id=request_text,
                    capsule_hash=capsule_hash,
                    deterministic_methods_considered=deterministic_methods_attempted,
                    deterministic_methods_executed=deterministic_methods_executed,
                    remaining_uncertainty=remaining_uncertainty,
                    candidate_count=candidate_count,
                    effective_budget=effective_budget,
                    actual_calls=0,
                    actual_input_tokens=None,
                    actual_output_tokens=None,
                    latency_ms=(time.perf_counter() - started_at) * 1000.0,
                    fallback_used=False,
                    error_class=None,
                )
                telemetry_event_id = _emit_gate_event(decision_event, telemetry_sink=telemetry_sink)
                return {
                    "decision": decision,
                    "authorized": False,
                    "reason_code": reason_code,
                    "boundary_id": boundary_text,
                    "caller_id": caller_text,
                    "purpose_code": purpose_text,
                    "request_id": request_text,
                    "capsule_hash": capsule_hash,
                    "capsule_valid": capsule_valid,
                    "capsule_errors": capsule_errors,
                    "deterministic_methods_attempted": deterministic_methods_attempted,
                    "remaining_uncertainty": remaining_uncertainty,
                    "candidate_count": candidate_count,
                    "authorized_mode": authorized_mode,
                    "effective_budget": effective_budget,
                    "telemetry_event_id": telemetry_event_id,
                    "evaluation_event_id": evaluation_event_id,
                    "boundary_registry": registry,
                    "boundary_entry": boundary_entry,
                    "boundary_policy": merged_policy,
                    "deterministic_attempt_record": attempt,
                    "uncertainty_record": uncertainty,
                    "candidate_set": candidate_values,
                    "cache_lookup": cache_lookup_payload,
                    "cached_result": cached_result,
                    "cache_hit": True,
                }

    decision = "DENY_BOUNDARY_NOT_REGISTERED"
    reason_code = decision
    authorized = False
    authorized_mode = "NONE"
    error_class = "NONE"

    if boundary_entry is None:
        reason_code = "DENY_BOUNDARY_NOT_REGISTERED"
    elif registry_errors:
        decision = reason_code = "DENY_CONTEXT_INVALID"
        error_class = "CONFIGURATION_ERROR"
    elif not _boundary_status_allows_inference(str(merged_policy.get("status", ""))):
        reason_code = "DENY_AUTHORITY_INVALID"
    elif merged_policy and not _resolve_call_or_purpose_allowed(_normalize_string_list(merged_policy.get("allowed_callers")), caller_text):
        reason_code = "DENY_CALLER_NOT_ALLOWED"
    elif merged_policy and not _resolve_call_or_purpose_allowed(_normalize_string_list(merged_policy.get("allowed_purposes")), purpose_text):
        reason_code = "DENY_PURPOSE_NOT_ALLOWED"
    elif not capsule_valid:
        reason_code = "DENY_CONTEXT_INVALID"
        error_class = "CAPSULE_VALIDATION_ERROR"
    elif not attempt["is_well_formed"] or not attempt["methods_considered"]:
        reason_code = "DENY_CONTEXT_INVALID"
    elif attempt["deterministic_answer_available"]:
        reason_code = "DENY_DETERMINISTIC_RESULT_AVAILABLE"
    elif attempt["cache_answer_available"]:
        reason_code = "DENY_CACHE_RESULT_AVAILABLE"
    elif attempt["machine_readable_resolution_available"]:
        reason_code = "DENY_MACHINE_READABLE_STRUCTURE"
    elif attempt["finite_candidate_resolution_available"]:
        reason_code = "DENY_FINITE_SEARCH_AVAILABLE"
    elif attempt["failure_signature_resolution_available"]:
        reason_code = "DENY_KNOWN_FAILURE_SIGNATURE"
    elif _materiality_rank(uncertainty["materiality"]) < MATERIALITY_RANK["MEDIUM"]:
        reason_code = "DENY_UNCERTAINTY_NOT_MATERIAL"
    else:
        budget_ok, budget_reason = _evaluate_budget(request_budget, budget_ceiling)
        if not budget_ok:
            reason_code = budget_reason
        elif not candidate_count:
            reason_code = "DENY_FINITE_SEARCH_AVAILABLE"
        elif "CONSTRAINED" not in _normalize_string_list(merged_policy.get("allowed_modes"), DEFAULT_ALLOWED_MODES):
            reason_code = "DENY_AUTHORITY_INVALID"
        elif merged_policy.get("open_mode_enabled"):
            reason_code = "AUTHORIZE_OPEN_INFERENCE"
            authorized = True
            authorized_mode = "OPEN"
            decision = reason_code
        else:
            reason_code = "AUTHORIZE_CONSTRAINED_INFERENCE"
            authorized = True
            authorized_mode = "CONSTRAINED"
            decision = reason_code

    if not authorized:
        decision = reason_code

    evaluation_event = _build_gate_event(
        event_type="GATE_EVALUATED",
        decision=decision,
        reason_code=reason_code,
        boundary_id=boundary_text,
        caller_id=caller_text,
        purpose_code=purpose_text,
        request_id=request_text,
        capsule_hash=capsule_hash,
        deterministic_methods_considered=deterministic_methods_attempted,
        deterministic_methods_executed=deterministic_methods_executed,
        remaining_uncertainty=remaining_uncertainty,
        candidate_count=candidate_count,
        effective_budget=effective_budget,
        actual_calls=1 if authorized else 0,
        actual_input_tokens=None,
        actual_output_tokens=None,
        latency_ms=(time.perf_counter() - started_at) * 1000.0,
        fallback_used=not authorized,
        error_class=error_class if error_class != "NONE" else None,
    )
    evaluation_event_id = _emit_gate_event(evaluation_event, telemetry_sink=telemetry_sink)

    decision_event_type = "GATE_AUTHORIZED" if authorized else "GATE_DENIED"
    decision_event = _build_gate_event(
        event_type=decision_event_type,
        decision=decision,
        reason_code=reason_code,
        boundary_id=boundary_text,
        caller_id=caller_text,
        purpose_code=purpose_text,
        request_id=request_text,
        capsule_hash=capsule_hash,
        deterministic_methods_considered=deterministic_methods_attempted,
        deterministic_methods_executed=deterministic_methods_executed,
        remaining_uncertainty=remaining_uncertainty,
        candidate_count=candidate_count,
        effective_budget=effective_budget,
        actual_calls=1 if authorized else 0,
        actual_input_tokens=None,
        actual_output_tokens=None,
        latency_ms=(time.perf_counter() - started_at) * 1000.0,
        fallback_used=not authorized,
        error_class=error_class if error_class != "NONE" else None,
    )
    telemetry_event_id = _emit_gate_event(decision_event, telemetry_sink=telemetry_sink)

    return {
        "decision": decision,
        "authorized": bool(authorized),
        "reason_code": reason_code,
        "boundary_id": boundary_text,
        "caller_id": caller_text,
        "purpose_code": purpose_text,
        "request_id": request_text,
        "capsule_hash": capsule_hash,
        "capsule_valid": capsule_valid,
        "capsule_errors": capsule_errors,
        "deterministic_methods_attempted": deterministic_methods_attempted,
        "remaining_uncertainty": remaining_uncertainty,
        "candidate_count": candidate_count,
        "authorized_mode": authorized_mode,
        "effective_budget": effective_budget,
        "telemetry_event_id": telemetry_event_id,
        "evaluation_event_id": evaluation_event_id,
        "boundary_registry": registry,
        "boundary_entry": boundary_entry,
        "boundary_policy": merged_policy,
        "deterministic_attempt_record": attempt,
        "uncertainty_record": uncertainty,
        "candidate_set": candidate_values,
        "cache_lookup": cache_lookup_payload,
        "cached_result": cached_result,
        "cache_hit": False if cache_lookup_result is None else bool(getattr(cache_lookup_result, "hit", False)),
    }


def _find_line_range(path: Path, pattern: re.Pattern[str]) -> Optional[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    matches = [index + 1 for index, line in enumerate(lines) if pattern.search(line)]
    if not matches:
        return None
    return f"{matches[0]}-{matches[-1]}"


def _function_line_range(path: Path, function_name: str) -> Optional[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    start = None
    end = None
    for index, line in enumerate(lines):
        if start is None and re.match(rf"^def\s+{re.escape(function_name)}\s*\(", line):
            start = index + 1
            continue
        if start is not None and index + 1 > start:
            if re.match(r"^(def|class)\s+", line):
                end = index
                break
    if start is None:
        return None
    if end is None:
        end = len(lines)
    return f"{start}-{end}"


def scan_repository_inference_boundaries(root: Optional[str | Path] = None) -> Dict[str, Any]:
    root_path = Path(root) if root is not None else ROOT
    registry = load_inference_boundary_registry()
    registry_errors = validate_inference_boundary_registry_payload(registry)
    semantic_registry_entry = _load_boundary_entry("SEMANTIC_READOUT_OPTIONAL_OPENAI_001", registry)
    semantic_allowed_callers = _normalize_string_list(_first(semantic_registry_entry or {}, "allowed_callers", default=()))
    semantic_allowed_purposes = _normalize_string_list(_first(semantic_registry_entry or {}, "allowed_purposes", default=()))
    semantic_allowed_modes = _normalize_string_list(_first(semantic_registry_entry or {}, "allowed_modes", default=DEFAULT_ALLOWED_MODES), DEFAULT_ALLOWED_MODES)
    semantic_default_budget = _normalize_budget(_first(semantic_registry_entry or {}, "default_budget", default=DEFAULT_BUDGET))
    semantic_budget_ceiling = _normalize_budget(_first(semantic_registry_entry or {}, "budget_ceiling", default={"maximum_calls": 1, "maximum_retries": 1, "maximum_input_tokens": 12000, "maximum_output_tokens": 500, "maximum_latency_ms": 12000}))
    semantic_deterministic_fallback = _as_dict(_first(semantic_registry_entry or {}, "deterministic_fallback", default={"symbol": "_local_reply", "reply_source": "LOCAL_DETERMINISTIC"}))
    semantic_output_schema = str(_first(semantic_registry_entry or {}, "output_schema", default="semantic_readout_reply_v1"))
    semantic_telemetry_schema = str(_first(semantic_registry_entry or {}, "telemetry_schema", default="semantic_readout_boundary_event_v1"))
    semantic_retry_policy = _as_dict(_first(semantic_registry_entry or {}, "retry_policy", default={"default_retry_budget": 0, "automatic_retry": False}))
    semantic_authority_class = str(_first(semantic_registry_entry or {}, "authority_class", default="PRESENTATION_ONLY"))
    semantic_last_audited = _first(semantic_registry_entry or {}, "last_audited", default=None)

    code_roots = [
        root_path / "scripts",
        root_path / "tools",
        root_path / "tests",
        root_path / "gpt_folder_bridge",
    ]
    config_path = root_path / "tools" / "signal_scope_phase_continuation_engine" / "config" / "config_v14_terminal.json"
    semantic_path = root_path / "tools" / "signal_scope_phase_continuation_engine" / "core" / "semantic_readout.py"
    test_path = root_path / "tests" / "test_semantic_readout_capability_gate.py"
    bridge_path = root_path / "gpt_folder_bridge" / "bridge.py"

    candidate_paths: list[Path] = []
    for base in code_roots:
        if not base.exists():
            continue
        for suffix in ("*.py", "*.js", "*.mjs", "*.ts", "*.json", "*.md"):
            candidate_paths.extend(base.rglob(suffix))
    if config_path.exists():
        candidate_paths.append(config_path)
    candidate_paths = [path for path in dict.fromkeys(candidate_paths) if path.exists()]

    registered_boundaries = []
    test_only_surfaces = []
    activation_surfaces = []
    false_positives = []

    for path in candidate_paths:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(path.relative_to(root_path)).replace("\\", "/")
        if path == semantic_path:
            if any(pattern.search(text) for pattern in EXECUTABLE_BOUNDARY_PATTERNS):
                registered_boundaries.append(
                    {
                        "boundary_id": "SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
                        "path": rel,
                        "symbol": "_openai_compatible_reply",
                        "status": "LATENT",
                        "owner": "tools.signal_scope_phase_continuation_engine.core.semantic_readout",
                        "allowed_callers": list(semantic_allowed_callers),
                        "allowed_purposes": list(semantic_allowed_purposes),
                        "allowed_modes": list(semantic_allowed_modes),
                        "default_budget": semantic_default_budget,
                        "budget_ceiling": semantic_budget_ceiling,
                        "deterministic_fallback": semantic_deterministic_fallback,
                        "output_schema": semantic_output_schema,
                        "telemetry_schema": semantic_telemetry_schema,
                        "retry_policy": semantic_retry_policy,
                        "authority_class": semantic_authority_class,
                        "last_audited": semantic_last_audited or datetime.now(timezone.utc).isoformat(),
                        "line_range": _function_line_range(path, "_openai_compatible_reply"),
                    }
                )
        elif path == test_path:
            if any(pattern.search(text) for pattern in EXECUTABLE_BOUNDARY_PATTERNS):
                test_only_surfaces.append(
                    {
                        "path": rel,
                        "symbol": "SemanticReadoutCapabilityGateTests",
                        "classification": "TEST_ONLY",
                        "line_range": _find_line_range(path, re.compile(r"^class\s+SemanticReadoutCapabilityGateTests")),
                    }
                )
        elif path == config_path:
            if any(pattern.search(text) for pattern in CONFIG_ACTIVATION_PATTERNS):
                activation_surfaces.append(
                    {
                        "path": rel,
                        "symbol": "semantic_readout",
                        "classification": "LATENT_CONFIGURATION",
                        "line_range": _find_line_range(path, re.compile(r'"semantic_readout"\s*:')),
                    }
                )
        elif path == bridge_path:
            if "API_KEY = \"change-this-long-random-key\"" in text:
                false_positives.append(
                    {
                        "path": rel,
                        "symbol": "API_KEY",
                        "classification": "FALSE_POSITIVE",
                        "reason": "Local authenticated file bridge stub; no model/provider invocation.",
                        "line_range": _find_line_range(path, re.compile(r"API_KEY\s*=")),
                    }
                )

    if not registered_boundaries and semantic_path.exists() and any(pattern.search(semantic_path.read_text(encoding="utf-8", errors="ignore")) for pattern in EXECUTABLE_BOUNDARY_PATTERNS):
        registered_boundaries.append(
            {
                "boundary_id": "SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
                "path": str(semantic_path.relative_to(root_path)).replace("\\", "/"),
                "symbol": "_openai_compatible_reply",
                "status": "LATENT",
                "owner": "tools.signal_scope_phase_continuation_engine.core.semantic_readout",
                "allowed_callers": list(semantic_allowed_callers),
                "allowed_purposes": list(semantic_allowed_purposes),
                "allowed_modes": list(semantic_allowed_modes),
                "default_budget": semantic_default_budget,
                "budget_ceiling": semantic_budget_ceiling,
                "deterministic_fallback": semantic_deterministic_fallback,
                "output_schema": semantic_output_schema,
                "telemetry_schema": semantic_telemetry_schema,
                "retry_policy": semantic_retry_policy,
                "authority_class": semantic_authority_class,
                "last_audited": datetime.now(timezone.utc).isoformat(),
                "line_range": _function_line_range(semantic_path, "_openai_compatible_reply"),
            }
        )

    discovered_total = len(registered_boundaries) + len(test_only_surfaces) + len(activation_surfaces) + len(false_positives)
    return {
        "schema_id": "inference_boundary_scan_v1",
        "schema_version": "1.0.0",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "scan_root": str(root_path),
        "summary": {
            "boundaries_found": len(registered_boundaries),
            "test_only_surfaces": len(test_only_surfaces),
            "activation_surfaces": len(activation_surfaces),
            "false_positives": len(false_positives),
            "discovered_total": discovered_total,
        },
        "registered_boundaries": registered_boundaries,
        "test_only_surfaces": test_only_surfaces,
        "activation_surfaces": activation_surfaces,
        "false_positives": false_positives,
        "registry_errors": registry_errors,
    }
