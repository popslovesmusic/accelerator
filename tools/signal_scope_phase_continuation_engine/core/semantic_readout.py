from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import uuid
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Tuple

try:
    from scripts import query_governance as qg
except Exception:  # pragma: no cover - fallback only for constrained import environments
    qg = None

try:
    from tools.inference_governance import evaluate_inference_necessity_gate
except Exception:  # pragma: no cover - fallback only for constrained import environments
    evaluate_inference_necessity_gate = None


LOGGER = logging.getLogger(__name__)
_DEFAULT_ALLOWED_NETWORK_ENDPOINTS: Tuple[str, ...] = ("https://api.openai.com",)
_GOVERNED_CAPSULE_REQUIRED_SECTIONS: Tuple[str, ...] = (
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
)


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _first(mapping: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in mapping and mapping[k] is not None:
            return mapping[k]
    return default


def _clip01(x: Any) -> float:
    try:
        v = float(x)
    except Exception:
        return 0.0
    return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)


def _fmt(x: Any, ndigits: int = 3) -> str:
    try:
        return f"{float(x):.{int(ndigits)}f}"
    except Exception:
        return "n/a"


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def _approx_token_count(value: Any) -> int:
    text = value if isinstance(value, str) else _stable_json(value)
    if not text:
        return 0
    try:
        return max(1, (len(text.encode("utf-8")) + 3) // 4)
    except Exception:
        return 0


def _normalize_endpoint(value: Any) -> str:
    return str(value or "").strip().rstrip("/")


def _normalize_string_list(value: Any, default: Tuple[str, ...] = ()) -> Tuple[str, ...]:
    items = []
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    normalized = []
    for item in items:
        text = str(item or "").strip()
        if text and text not in normalized:
            normalized.append(text)
    return tuple(normalized) if normalized else tuple(default)


def _normalize_endpoint_list(value: Any) -> Tuple[str, ...]:
    items = []
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    normalized = []
    for item in items:
        endpoint = _normalize_endpoint(item)
        if endpoint and endpoint not in normalized:
            normalized.append(endpoint)
    return tuple(normalized) if normalized else _DEFAULT_ALLOWED_NETWORK_ENDPOINTS


def _bounded_projection(value: Any, *, depth: int = 2, max_items: int = 8) -> Any:
    if depth <= 0:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)
    if isinstance(value, dict):
        out: Dict[str, Any] = {}
        for index, key in enumerate(sorted(value.keys(), key=lambda item: str(item))):
            if index >= max_items:
                break
            out[str(key)] = _bounded_projection(value[key], depth=depth - 1, max_items=max_items)
        return out
    if isinstance(value, list):
        return [_bounded_projection(item, depth=depth - 1, max_items=max_items) for item in value[:max_items]]
    if isinstance(value, tuple):
        return [_bounded_projection(item, depth=depth - 1, max_items=max_items) for item in list(value)[:max_items]]
    if isinstance(value, set):
        return [_bounded_projection(item, depth=depth - 1, max_items=max_items) for item in sorted(value, key=str)[:max_items]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _capsule_id(capsule: Dict[str, Any]) -> str:
    direct = str(_first(capsule, "capsule_id", "capsule_hash", default="")).strip()
    if direct:
        return direct
    request_identity = _as_dict(_first(capsule, "request_identity", default={}))
    request_id = str(_first(request_identity, "request_id", "id", default="")).strip()
    if request_id:
        return request_id
    return ""


def _capsule_hash(capsule: Dict[str, Any]) -> str:
    direct = str(_first(capsule, "capsule_hash", default="")).strip()
    if direct:
        return direct
    try:
        hash_basis = _governed_context_capsule_hash_basis(capsule)
        if qg is not None and hasattr(qg, "_hash_json_value"):
            return str(qg._hash_json_value(hash_basis))
        return hashlib.sha256(_stable_json(hash_basis).encode("utf-8")).hexdigest()
    except Exception:
        return ""


def _governed_context_capsule_hash_basis(capsule: Dict[str, Any]) -> Dict[str, Any]:
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


def _governed_context_capsule_schema_validation_errors(capsule: Any) -> Tuple[list[str], str, str]:
    capsule_dict = _as_dict(capsule)
    expected_hash = ""
    expected_id = ""
    try:
        hash_basis = _governed_context_capsule_hash_basis(capsule_dict)
        if qg is not None and hasattr(qg, "_hash_json_value"):
            expected_hash = str(qg._hash_json_value(hash_basis))
        else:
            expected_hash = hashlib.sha256(_stable_json(hash_basis).encode("utf-8")).hexdigest()
        expected_id = f"{str(_first(capsule_dict, 'schema_id', default='governed_context_capsule_v1')).strip() or 'governed_context_capsule_v1'}:{expected_hash[:16]}"
    except Exception:
        expected_hash = ""
        expected_id = ""

    if qg is not None and hasattr(qg, "validate_governed_context_capsule_payload"):
        try:
            errors = list(qg.validate_governed_context_capsule_payload(capsule_dict, expected_hash=expected_hash or None, expected_id=expected_id or None))
        except Exception as exc:  # pragma: no cover - fallback only
            return [f"validation_exception:{exc.__class__.__name__}"], expected_hash, expected_id
        return errors, expected_hash, expected_id

    errors = []
    if not capsule_dict:
        errors.append("missing_governed_context_capsule")
    if expected_hash and str(_first(capsule_dict, "capsule_hash", default="")).strip() != expected_hash:
        errors.append("capsule_hash_mismatch")
    if expected_id and str(_first(capsule_dict, "capsule_id", default="")).strip() != expected_id:
        errors.append("capsule_id_mismatch")
    for section in _GOVERNED_CAPSULE_REQUIRED_SECTIONS:
        if section not in capsule_dict or capsule_dict[section] is None:
            errors.append(f"missing_capsule_section:{section}")
    return errors, expected_hash, expected_id


def _governed_context_capsule_is_valid(capsule: Any) -> Tuple[bool, str]:
    capsule_dict = _as_dict(capsule)
    if not capsule_dict:
        return False, "CAPSULE_MISSING"

    errors, expected_hash, expected_id = _governed_context_capsule_schema_validation_errors(capsule_dict)
    if errors:
        if "capsule_hash_mismatch" in errors:
            return False, "CAPSULE_HASH_INVALID"
        if "capsule_id_mismatch" in errors:
            return False, "CAPSULE_INVALID"
        if any(error.startswith("missing_top_level_field:capsule_hash") for error in errors):
            return False, "CAPSULE_MISSING"
        if any(error.startswith("missing_top_level_field:") or error.startswith("missing_capsule_section:") for error in errors):
            return False, "CAPSULE_INVALID"
        return False, "CAPSULE_INVALID"

    if expected_hash and str(_first(capsule_dict, "capsule_hash", default="")).strip() != expected_hash:
        return False, "CAPSULE_HASH_INVALID"

    return True, "CAPSULE_VALID"


def _governed_context_capsule_projection(
    *,
    capsule: Dict[str, Any],
    runtime_output: Dict[str, Any],
    prompt: str,
    include_prompt_content: bool = False,
) -> Dict[str, Any]:
    capsule_dict = _as_dict(capsule)
    selected_sections = {
        section: _bounded_projection(capsule_dict[section], depth=2, max_items=8)
        for section in _GOVERNED_CAPSULE_REQUIRED_SECTIONS
        if section in capsule_dict
    }
    included_field_paths = [f"capsule.{section}" for section in _GOVERNED_CAPSULE_REQUIRED_SECTIONS if section in capsule_dict]
    included_field_paths.extend(
        [
            "runtime_output.state.signature",
            "runtime_output.state.orientation",
            "runtime_output.state.reasoning",
            "runtime_output.output",
            "prompt.summary",
        ]
    )
    excluded_field_paths = [f"capsule.{key}" for key in sorted(capsule_dict.keys(), key=str) if key not in _GOVERNED_CAPSULE_REQUIRED_SECTIONS]
    if not include_prompt_content:
        excluded_field_paths.append("prompt.text")
    else:
        included_field_paths.append("prompt.text")

    projection = {
        "source_capsule_id": _capsule_id(capsule_dict),
        "source_capsule_schema_version": str(
            _first(capsule_dict, "capsule_schema_version", "schema_version", default="governed_context_capsule_v1")
        ),
        "source_capsule_hash": str(_first(capsule_dict, "capsule_hash", default="")).strip(),
        "included_field_paths": included_field_paths,
        "excluded_field_paths": excluded_field_paths,
        "selected_sections": selected_sections,
        "runtime_summary": _extract_runtime_summary(runtime_output),
        "prompt_summary": {
            "prompt_bytes": len((prompt or "").encode("utf-8")),
            "estimated_prompt_tokens": _approx_token_count(prompt or ""),
        },
    }
    serialized_projection = _stable_json(projection)
    projection["serialized_bytes"] = len(serialized_projection.encode("utf-8"))
    projection["estimated_tokens"] = _approx_token_count(serialized_projection)
    projection["projection_hash"] = hashlib.sha256(serialized_projection.encode("utf-8")).hexdigest()
    return projection


def _build_network_request_payload(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    cfg: "SemanticReadoutConfig",
    capsule_projection: Dict[str, Any],
    purpose_code: str = "",
) -> Dict[str, Any]:
    summary = _extract_runtime_summary(runtime_output)
    system = (
        "You are a helpful high-school science tutor. "
        "Answer concisely (2-5 sentences), use simple language, and ask 1 short follow-up question. "
        "If you are uncertain, say so briefly. "
        "Do not mention internal engine implementation unless the user asks."
    )
    user_projection = {
        "prompt": prompt,
        "purpose_code": purpose_code,
        "runtime_summary": summary,
        "governed_context_capsule_projection": capsule_projection,
    }
    user = _stable_json(user_projection)
    return {
        "model": cfg.openai_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.4,
        "max_tokens": 200,
    }


def _build_boundary_telemetry_event(
    *,
    event_type: str,
    caller_id: str,
    purpose_code: str,
    configured_backend: str,
    model_id: str,
    capability_enabled: bool,
    authorization_result: str,
    authorization_reason: str,
    capsule_hash: str,
    projection_hash: Optional[str],
    input_bytes: int,
    estimated_input_tokens: Optional[int],
    actual_input_tokens_if_reported: Optional[int],
    actual_output_tokens_if_reported: Optional[int],
    requested_output_limit: Optional[int],
    latency_ms: Optional[float],
    network_attempted: bool,
    outcome: str,
    fallback_used: bool,
    error_class: Optional[str],
    retry_count: int,
) -> Dict[str, Any]:
    return {
        "event_type": event_type,
        "event_id": uuid.uuid4().hex,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "caller_id": caller_id,
        "purpose_code": purpose_code,
        "configured_backend": configured_backend,
        "model_id": model_id,
        "capability_enabled": bool(capability_enabled),
        "authorization_result": authorization_result,
        "authorization_reason": authorization_reason,
        "capsule_hash": capsule_hash,
        "projection_hash": projection_hash,
        "input_bytes": int(input_bytes),
        "estimated_input_tokens": estimated_input_tokens,
        "actual_input_tokens_if_reported": actual_input_tokens_if_reported,
        "actual_output_tokens_if_reported": actual_output_tokens_if_reported,
        "requested_output_limit": requested_output_limit,
        "latency_ms": None if latency_ms is None else float(latency_ms),
        "network_attempted": bool(network_attempted),
        "outcome": outcome,
        "fallback_used": bool(fallback_used),
        "error_class": error_class,
        "retry_count": int(retry_count),
    }


def _emit_boundary_telemetry(event: Dict[str, Any], telemetry_sink: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
    try:
        LOGGER.info("%s", _stable_json(event))
    except Exception:
        pass
    if telemetry_sink is None:
        return
    try:
        telemetry_sink(dict(event))
    except Exception:
        pass


def _is_network_backend(backend: str) -> bool:
    return (backend or "").strip().lower() in {"openai", "openai_compatible"}


def _semantic_readout_shared_gate_request_id(*, prompt: str, runtime_output: Dict[str, Any], capsule_hash: str) -> str:
    basis = {
        "prompt_tokens": _approx_token_count(prompt or ""),
        "runtime_summary": _extract_runtime_summary(runtime_output),
        "capsule_hash": capsule_hash,
    }
    return f"semantic-readout:{hashlib.sha256(_stable_json(basis).encode('utf-8')).hexdigest()[:16]}"


def _semantic_readout_deterministic_attempt_record(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    cfg: "SemanticReadoutConfig",
    capsule_dict: Dict[str, Any],
    capsule_valid: bool,
    capsule_reason: str,
    capsule_errors: Optional[Tuple[str, ...]] = None,
) -> Dict[str, Any]:
    summary = _extract_runtime_summary(runtime_output)
    attempt_results = {
        "CONSTANT_CONFIGURATION": {
            "backend": (cfg.backend or "local").strip().lower(),
            "network_enabled": bool(cfg.enable_network_semantic_readout),
            "caller_allowlist_size": len(_normalize_string_list(cfg.allowed_callers)),
            "purpose_allowlist_size": len(_normalize_string_list(cfg.allowed_purposes)),
        },
        "LOOKUP": {
            "capsule_present": bool(capsule_dict),
            "capsule_reason": capsule_reason,
            "capsule_valid": bool(capsule_valid),
        },
        "CACHE": {
            "cache_answer_available": False,
            "cache_scope": "not used by semantic readout",
        },
        "RULE_ENGINE": {
            "caller_allowed": bool(_normalize_string_list(cfg.allowed_callers)),
            "purpose_allowed": bool(_normalize_string_list(cfg.allowed_purposes)),
            "endpoint": _normalize_endpoint(cfg.openai_base_url),
        },
        "SCHEMA_VALIDATION": {
            "capsule_errors": list(capsule_errors or ()),
        },
        "ERROR_SIGNATURE_CLASSIFICATION": {
            "selected_class": _first(_extract_runtime_summary(runtime_output), "selected_class", default="n/a"),
            "confidence": _first(summary, "confidence", default="n/a"),
            "hold": _first(summary, "hold", default=False),
        },
    }
    return {
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
        "results": attempt_results,
        "deterministic_answer_available": False,
        "cache_answer_available": False,
        "machine_readable_resolution_available": False,
        "finite_candidate_resolution_available": False,
        "failure_signature_resolution_available": False,
        "explanation": (
            "The shared necessity gate evaluates the optional network readout only after deterministic local readout, "
            "capsule validation, and bounded candidate construction do not settle the request."
        ),
    }


def _semantic_readout_uncertainty_record(
    *,
    runtime_output: Dict[str, Any],
    prompt: str,
    capsule_hash: str,
) -> Dict[str, Any]:
    summary = _extract_runtime_summary(runtime_output)
    confidence = summary.get("confidence", "n/a")
    caution = summary.get("caution", "n/a")
    raw_caution = summary.get("raw_caution", "n/a")
    hold = bool(summary.get("hold", False))
    try:
        confidence_value = float(confidence)
    except Exception:
        confidence_value = 0.0
    try:
        caution_value = float(caution)
    except Exception:
        caution_value = 0.0
    try:
        raw_caution_value = float(raw_caution)
    except Exception:
        raw_caution_value = 0.0

    if hold or confidence_value < 0.85 or caution_value >= 0.5 or raw_caution_value >= 0.5:
        materiality = "HIGH"
    elif confidence_value < 0.95:
        materiality = "MEDIUM"
    else:
        materiality = "LOW"

    return {
        "uncertainty_id": f"semantic-readout:{capsule_hash[:16] or 'no-capsule'}",
        "description": (
            "The runtime summary retains unresolved orientation and caution structure beyond the local deterministic reply."
        ),
        "materiality": materiality,
        "resolution_need": "OPTIONAL_PRESENTATION",
        "known_bounds": {
            "selected_class": summary.get("selected_class"),
            "confidence": confidence,
            "caution": caution,
            "raw_caution": raw_caution,
            "hold": hold,
        },
        "unresolved_dimensions": [
            "selected_class",
            "confidence",
            "caution",
            "hold",
        ],
        "consequence_of_no_inference": "Return the deterministic local reply and leave optional semantic commentary unresolved.",
    }


def _semantic_readout_inference_budget(cfg: "SemanticReadoutConfig", preview_metrics: Dict[str, Any]) -> Dict[str, int]:
    if int(cfg.network_retry_budget) <= 0:
        return {
            "maximum_calls": 0,
            "maximum_retries": 0,
            "maximum_input_tokens": 0,
            "maximum_output_tokens": 0,
            "maximum_latency_ms": 0,
        }
    return {
        "maximum_calls": max(1, int(cfg.network_retry_budget)),
        "maximum_retries": max(1, int(cfg.network_retry_budget)),
        "maximum_input_tokens": max(1, int(preview_metrics.get("estimated_input_tokens", 0) or 0)),
        "maximum_output_tokens": max(1, int(preview_metrics.get("requested_output_limit", 0) or 0)),
        "maximum_latency_ms": max(1, int(round(float(cfg.openai_timeout_s) * 1000.0))),
    }


def _semantic_readout_shared_gate_reason(result: Dict[str, Any]) -> str:
    reason = str(_first(result, "reason_code", default="NOT_REQUESTED")).strip()
    if reason.startswith("AUTHORIZE_"):
        return "AUTHORIZED"
    if reason == "DENY_CONTEXT_INVALID":
        capsule_errors = list(_first(result, "capsule_errors", default=[]) or [])
        if "capsule_hash_mismatch" in capsule_errors:
            return "CAPSULE_HASH_INVALID"
        if any(error.startswith("missing_top_level_field:capsule_hash") for error in capsule_errors):
            return "CAPSULE_MISSING"
        if any(error.startswith("missing_top_level_field:") or error.startswith("missing_capsule_section:") for error in capsule_errors):
            return "CAPSULE_INVALID"
        return "CAPSULE_INVALID"
    mapping = {
        "DENY_BOUNDARY_NOT_REGISTERED": "CAPABILITY_DISABLED",
        "DENY_AUTHORITY_INVALID": "BACKEND_NOT_EXPLICIT",
        "DENY_CALLER_NOT_ALLOWED": "CALLER_NOT_ALLOWED",
        "DENY_PURPOSE_NOT_ALLOWED": "PURPOSE_NOT_ALLOWED",
        "DENY_BUDGET_EXHAUSTED": "BUDGET_EXHAUSTED",
        "DENY_DETERMINISTIC_RESULT_AVAILABLE": "DETERMINISTIC_RESULT_AVAILABLE",
        "DENY_CACHE_RESULT_AVAILABLE": "CACHE_RESULT_AVAILABLE",
        "DENY_MACHINE_READABLE_STRUCTURE": "MACHINE_READABLE_STRUCTURE",
        "DENY_FINITE_SEARCH_AVAILABLE": "FINITE_SEARCH_AVAILABLE",
        "DENY_KNOWN_FAILURE_SIGNATURE": "KNOWN_FAILURE_SIGNATURE",
        "DENY_UNCERTAINTY_NOT_MATERIAL": "UNCERTAINTY_NOT_MATERIAL",
    }
    return mapping.get(reason, reason or "NOT_REQUESTED")


def _semantic_readout_capability_gate(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    cfg: "SemanticReadoutConfig",
    caller_id: Optional[str],
    purpose_code: Optional[str],
    governed_context_capsule: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    backend = (cfg.backend or "local").strip().lower()
    model_id = str(cfg.openai_model or "").strip()
    caller_text = str(caller_id or "").strip()
    purpose_text = str(purpose_code or "").strip()
    capsule_dict = _as_dict(governed_context_capsule)
    capsule_hash = _capsule_hash(capsule_dict) if capsule_dict else ""
    capsule_projection = _governed_context_capsule_projection(
        capsule=capsule_dict,
        runtime_output=runtime_output,
        prompt=prompt,
        include_prompt_content=bool(cfg.log_prompt_content),
    ) if capsule_dict else {}
    preview_payload = _build_network_request_payload(
        prompt=prompt,
        runtime_output=runtime_output,
        cfg=cfg,
        capsule_projection=capsule_projection,
        purpose_code=purpose_text,
    )
    preview_payload_bytes = _stable_json(preview_payload).encode("utf-8")
    projection_hash = str(_first(capsule_projection, "projection_hash", default="")).strip() or None
    preview_metrics = {
        "input_bytes": len(preview_payload_bytes),
        "estimated_input_tokens": _approx_token_count(preview_payload),
        "requested_output_limit": int(_first(preview_payload, "max_tokens", default=0) or 0),
    }
    network_requested = bool(cfg.enable_network_semantic_readout) and _is_network_backend(backend)
    valid_capsule, capsule_reason = _governed_context_capsule_is_valid(capsule_dict)
    attempt_record = _semantic_readout_deterministic_attempt_record(
        prompt=prompt,
        runtime_output=runtime_output,
        cfg=cfg,
        capsule_dict=capsule_dict,
        capsule_valid=valid_capsule,
        capsule_reason=capsule_reason,
        capsule_errors=tuple(_governed_context_capsule_schema_validation_errors(capsule_dict)[0]) if capsule_dict else (),
    )
    uncertainty_record = _semantic_readout_uncertainty_record(
        runtime_output=runtime_output,
        prompt=prompt,
        capsule_hash=capsule_hash,
    )
    inference_budget = _semantic_readout_inference_budget(cfg, preview_metrics)
    candidate_set = [backend] if network_requested else []
    shared_gate = {
        "decision": "DENY_BOUNDARY_NOT_REGISTERED",
        "authorized": False,
        "reason_code": "DENY_BOUNDARY_NOT_REGISTERED",
        "authorized_mode": "NONE",
        "telemetry_event_id": "",
        "evaluation_event_id": "",
        "effective_budget": dict(inference_budget),
    }
    subordinate_reason = "AUTHORIZED"
    if not cfg.enable_network_semantic_readout:
        subordinate_reason = "CAPABILITY_DISABLED"
    elif backend == "local":
        subordinate_reason = "BACKEND_LOCAL"
    elif not _is_network_backend(backend):
        subordinate_reason = "BACKEND_NOT_EXPLICIT"
    elif not model_id:
        subordinate_reason = "MODEL_MISSING"
    elif _normalize_endpoint(cfg.openai_base_url) not in _normalize_endpoint_list(cfg.allowed_network_endpoints):
        subordinate_reason = "ENDPOINT_NOT_PERMITTED"
    elif not (os.environ.get("SEMANTIC_READOUT_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        subordinate_reason = "CREDENTIAL_MISSING"
    elif not caller_text:
        subordinate_reason = "CALLER_MISSING"
    elif not _normalize_string_list(cfg.allowed_callers) or caller_text not in _normalize_string_list(cfg.allowed_callers):
        subordinate_reason = "CALLER_NOT_ALLOWED"
    elif not purpose_text:
        subordinate_reason = "PURPOSE_MISSING"
    elif not _normalize_string_list(cfg.allowed_purposes) or purpose_text not in _normalize_string_list(cfg.allowed_purposes):
        subordinate_reason = "PURPOSE_NOT_ALLOWED"
    elif not valid_capsule:
        subordinate_reason = capsule_reason
    elif int(cfg.network_retry_budget) <= 0:
        subordinate_reason = "BUDGET_EXHAUSTED"

    authorized = False
    authorization_reason = subordinate_reason if subordinate_reason != "AUTHORIZED" else "NOT_REQUESTED"
    if network_requested and subordinate_reason == "AUTHORIZED" and evaluate_inference_necessity_gate is not None:
        shared_gate = evaluate_inference_necessity_gate(
            boundary_id="SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
            caller_id=caller_text,
            purpose_code=purpose_text,
            request_id=_semantic_readout_shared_gate_request_id(prompt=prompt, runtime_output=runtime_output, capsule_hash=capsule_hash),
            governed_context_capsule=capsule_dict,
            deterministic_attempt_record=attempt_record,
            uncertainty_record=uncertainty_record,
            candidate_set=candidate_set,
            inference_budget=inference_budget,
            telemetry_sink=None,
        )
        authorized = bool(_first(shared_gate, "authorized", default=False))
        authorization_reason = _semantic_readout_shared_gate_reason(shared_gate)
    elif network_requested and subordinate_reason == "AUTHORIZED":
        authorization_reason = "DENY_BOUNDARY_NOT_REGISTERED"
    elif not network_requested:
        authorization_reason = "CAPABILITY_DISABLED" if not cfg.enable_network_semantic_readout else (
            "BACKEND_LOCAL" if backend == "local" else (
                "BACKEND_NOT_EXPLICIT" if not _is_network_backend(backend) else "NOT_REQUESTED"
            )
        )

    authorization_result = "AUTHORIZED" if authorized else ("DENIED" if network_requested else "NOT_REQUESTED")
    remaining_budget = max(0, int(cfg.network_retry_budget) - (1 if authorized else 0))
    shared_reason_code = str(_first(shared_gate, "reason_code", default="DENY_BOUNDARY_NOT_REGISTERED" if network_requested else "NOT_REQUESTED")).strip()

    return {
        "authorized": bool(authorized),
        "authorization_result": authorization_result if authorized else ("NOT_REQUESTED" if not network_requested else "DENIED"),
        "authorization_reason": authorization_reason,
        "normalized_backend": backend,
        "normalized_model": model_id,
        "caller_id": caller_text,
        "purpose_code": purpose_text,
        "capsule_hash": capsule_hash,
        "capsule_projection": capsule_projection,
        "projection_hash": projection_hash,
        "preview_payload": preview_payload,
        "preview_metrics": preview_metrics,
        "requested_output_limit": int(preview_metrics["requested_output_limit"]),
        "remaining_budget": remaining_budget,
        "network_requested": network_requested,
        "shared_gate_decision": _first(shared_gate, "decision", default="DENY_BOUNDARY_NOT_REGISTERED"),
        "shared_gate_reason_code": shared_reason_code,
        "shared_gate_authorized_mode": _first(shared_gate, "authorized_mode", default="NONE"),
        "shared_gate_telemetry_event_id": _first(shared_gate, "telemetry_event_id", default=""),
        "shared_gate_evaluation_event_id": _first(shared_gate, "evaluation_event_id", default=""),
        "shared_gate_effective_budget": dict(_first(shared_gate, "effective_budget", default=inference_budget) or inference_budget),
        "deterministic_attempt_record": attempt_record,
        "uncertainty_record": uncertainty_record,
        "candidate_set": list(candidate_set),
        "inference_budget": dict(inference_budget),
    }


def _network_authorization(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    cfg: "SemanticReadoutConfig",
    caller_id: Optional[str],
    governed_context_capsule: Optional[Dict[str, Any]],
) -> Tuple[bool, str, str, str, Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    gate = _semantic_readout_capability_gate(
        prompt=prompt,
        runtime_output=runtime_output,
        cfg=cfg,
        caller_id=caller_id,
        purpose_code=None,
        governed_context_capsule=governed_context_capsule,
    )
    return (
        bool(gate["authorized"]),
        str(gate["authorization_result"]),
        str(gate["authorization_reason"]),
        str(gate["capsule_hash"]),
        dict(gate["capsule_projection"]),
        dict(gate["preview_payload"]),
        dict(gate["preview_metrics"]),
    )


@dataclass(frozen=True)
class SemanticReadoutConfig:
    enabled: bool = True
    backend: str = "local"  # local | openai_compatible
    style: str = "hs_science"
    max_sentences: int = 4
    include_followup_question: bool = True
    caution_hedge_threshold: float = 0.65
    hold_explain: bool = True
    openai_base_url: str = "https://api.openai.com"
    openai_model: str = ""
    openai_timeout_s: float = 12.0
    enable_network_semantic_readout: bool = False
    allowed_network_endpoints: Tuple[str, ...] = _DEFAULT_ALLOWED_NETWORK_ENDPOINTS
    network_retry_budget: int = 0
    allowed_callers: Tuple[str, ...] = ()
    allowed_purposes: Tuple[str, ...] = ()
    telemetry_enabled: bool = True
    log_prompt_content: bool = False


def _load_cfg(config: Optional[Dict[str, Any]]) -> SemanticReadoutConfig:
    cfg = _as_dict(config or {})
    sr = _as_dict(_first(cfg, "semantic_readout", default={}))
    oc = _as_dict(_first(sr, "openai_compatible", "openai", default={}))
    return SemanticReadoutConfig(
        enabled=bool(_first(sr, "enabled", default=True)),
        backend=str(_first(sr, "backend", default="local")),
        style=str(_first(sr, "style", default="hs_science")),
        max_sentences=int(_first(sr, "max_sentences", default=4)),
        include_followup_question=bool(_first(sr, "include_followup_question", default=True)),
        caution_hedge_threshold=float(_first(sr, "caution_hedge_threshold", default=0.65)),
        hold_explain=bool(_first(sr, "hold_explain", default=True)),
        openai_base_url=str(_first(oc, "base_url", default="https://api.openai.com")).rstrip("/"),
        openai_model=str(_first(oc, "model", default="")),
        openai_timeout_s=float(_first(oc, "timeout_s", default=12.0)),
        enable_network_semantic_readout=bool(_first(sr, "enable_network_semantic_readout", default=False)),
        allowed_network_endpoints=_normalize_endpoint_list(
            _first(sr, "allowed_network_endpoints", "permitted_network_endpoints", default=_DEFAULT_ALLOWED_NETWORK_ENDPOINTS)
        ),
        network_retry_budget=int(_first(sr, "network_retry_budget", "retry_budget", default=0)),
        allowed_callers=_normalize_string_list(_first(sr, "allowed_callers", "permitted_callers", default=())),
        allowed_purposes=_normalize_string_list(_first(sr, "allowed_purposes", "permitted_purposes", default=())),
        telemetry_enabled=bool(_first(sr, "telemetry_enabled", default=True)),
        log_prompt_content=bool(_first(sr, "log_prompt_content", default=False)),
    )


def _extract_runtime_summary(runtime_output: Dict[str, Any]) -> Dict[str, Any]:
    state = _as_dict(_first(runtime_output, "state", default={}))
    signature = _as_dict(_first(state, "signature", default={}))
    orientation = _as_dict(_first(state, "orientation", default={}))
    reasoning = _as_dict(_first(state, "reasoning", default={}))
    out = _as_dict(_first(runtime_output, "output", default={}))

    caution = _clip01(_first(signature, "caution_scalar", default=0.0))
    raw_caution = _clip01(_first(signature, "raw_caution_scalar", default=0.0))
    recovery = _clip01(_first(signature, "recovery_scalar", default=0.0))
    hold = bool(_first(signature, "hold_state", default=False))

    return {
        "selected_class": _first(out, "selected_class", default="n/a"),
        "confidence": _first(out, "confidence", default="n/a"),
        "operator": _first(orientation, "active_operator", default="n/a"),
        "active_component_id": _first(signature, "active_component_id", default="n/a"),
        "component_count": len(_first(signature, "components", default=[]) or []),
        "caution": float(caution),
        "raw_caution": float(raw_caution),
        "recovery": float(recovery),
        "hold": bool(hold),
        "hold_semantics": _first(reasoning, "hold_semantics", default="n/a"),
    }


_SCIENCE_SNIPPETS: Tuple[Tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bphotosynthesis\b", re.I), "Photosynthesis is how plants use sunlight to turn water and carbon dioxide into sugar (stored energy), releasing oxygen as a byproduct."),
    (re.compile(r"\brespiration\b", re.I), "Cellular respiration is how cells break down sugar to make usable energy (ATP), usually using oxygen and producing carbon dioxide and water."),
    (re.compile(r"\bmitosis\b", re.I), "Mitosis is cell division that makes two identical cells, used for growth and repair."),
    (re.compile(r"\bmeiosis\b", re.I), "Meiosis is cell division that makes sperm/egg cells with half the DNA, creating genetic variation."),
    (re.compile(r"\bdna\b", re.I), "DNA is the molecule that stores genetic instructions. Genes are DNA segments that help build proteins."),
    (re.compile(r"\bevolution\b", re.I), "Evolution is change in a population over generations. Natural selection favors traits that help survival and reproduction in a given environment."),
    (re.compile(r"\bgravity\b", re.I), "Gravity is the attractive force between masses. On Earth, it pulls objects toward the planet's center."),
    (re.compile(r"\bsky\b.*\bblue\b|\bwhy\b.*\bsky\b.*\bblue\b", re.I), "The sky looks blue because air molecules scatter short-wavelength (blue) light more than long-wavelength (red) light (Rayleigh scattering)."),
    (re.compile(r"\bplate tectonics\b|\btectonic\b", re.I), "Plate tectonics explains how Earth's crust is split into moving plates, causing earthquakes, volcanoes, and mountain building."),
    (re.compile(r"\bclimate change\b|\bglobal warming\b", re.I), "Climate change is long-term warming and related shifts in weather patterns, mainly driven today by increased greenhouse gases from human activity."),
    (re.compile(r"\bchemical reaction\b|\breaction\b", re.I), "A chemical reaction rearranges atoms: old bonds break and new bonds form. Matter is conserved even though substances change."),
)


def _is_greeting(text: str) -> bool:
    t = (text or "").strip().lower()
    return t in {"hello", "hi", "hey", "yo"}


def _is_thanks(text: str) -> bool:
    t = (text or "").strip().lower()
    return t in {"thanks", "thank you", "thx"}


def _is_question(text: str) -> bool:
    t = (text or "").strip()
    return t.endswith("?") or t.lower().startswith(("why ", "how ", "what ", "when ", "where "))


def _local_reply(*, prompt: str, runtime_output: Dict[str, Any], cfg: SemanticReadoutConfig) -> str:
    summary = _extract_runtime_summary(runtime_output)
    caution = float(summary["caution"])
    recovery = float(summary["recovery"])
    hold = bool(summary["hold"])

    if _is_greeting(prompt):
        return "Hi - ask me a science question (biology, chemistry, physics, Earth/space), and I'll explain it in a few sentences."
    if _is_thanks(prompt):
        return "You're welcome."

    snippet = None
    for pat, text in _SCIENCE_SNIPPETS:
        if pat.search(prompt or ""):
            snippet = text
            break

    hedge = caution >= float(cfg.caution_hedge_threshold)
    sentences = []

    if snippet:
        sentences.append(snippet)
    else:
        if _is_question(prompt):
            sentences.append("Here's a quick high-school level take, plus what the v14 engine is doing under the hood.")
        else:
            sentences.append("Got it. Here's a short explanation and a quick state readback from the v14 engine.")

    if hedge:
        sentences.append("I'm being a bit cautious here (moderate caution), so I may need one more detail to be precise.")

    if cfg.hold_explain and hold:
        sentences.append("The engine is in HOLD, meaning it's intentionally avoiding major state updates for stability.")

    sentences.append(
        "Engine snapshot: "
        f"op={summary['operator']} "
        f"comp={summary['active_component_id']} "
        f"caution={_fmt(caution)} "
        f"recovery={_fmt(recovery)} "
        f"conf={_fmt(summary['confidence'])}."
    )

    if cfg.include_followup_question:
        if snippet:
            sentences.append("Want an example, a diagram-style description, or a practice question?")
        else:
            sentences.append("What grade level and which part should we focus on (definition, mechanism, or example)?")

    max_s = max(1, int(cfg.max_sentences))
    return " ".join(sentences[:max_s]).strip()


def _classify_semantic_readout_failure(exc: BaseException, *, content: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> str:
    if data is not None and not isinstance(data, dict):
        return "PROVIDER_RESPONSE_ERROR"
    if isinstance(content, str) and not content.strip():
        return "MODEL_OUTPUT_EMPTY"
    if isinstance(exc, urllib.error.HTTPError):
        return "HTTP_ERROR"
    if isinstance(exc, TimeoutError):
        return "NETWORK_TIMEOUT"
    if isinstance(exc, urllib.error.URLError):
        reason = getattr(exc, "reason", None)
        if isinstance(reason, TimeoutError):
            return "NETWORK_TIMEOUT"
        return "NETWORK_CONNECTION_ERROR"
    if isinstance(exc, json.JSONDecodeError):
        return "PROVIDER_RESPONSE_ERROR"
    if isinstance(exc, (ValueError, KeyError)):
        return "PROVIDER_RESPONSE_ERROR"
    if isinstance(exc, OSError):
        return "NETWORK_CONNECTION_ERROR"
    return "UNKNOWN_NETWORK_ERROR"


def _semantic_readout_reply_record(
    *,
    reply_text: str,
    reply_source: str,
    backend_status: str,
    authorization_reason: str,
    caller_id: str,
    purpose_code: str,
    capsule_hash: str,
    fallback_used: bool,
    telemetry_event_id: str,
    summary_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "schema_id": "semantic_readout_reply_v1",
        "schema_version": "1.0.0",
        "reply_text": reply_text,
        "reply_source": reply_source,
        "summary_id": summary_id,
        "backend_status": backend_status,
        "authorization_reason": authorization_reason,
        "caller_id": caller_id,
        "purpose_code": purpose_code,
        "capsule_hash": capsule_hash,
        "fallback_used": bool(fallback_used),
        "telemetry_event_id": telemetry_event_id,
    }


def _emit_semantic_readout_event(
    *,
    cfg: SemanticReadoutConfig,
    gate: Dict[str, Any],
    event_type: str,
    outcome: str,
    fallback_used: bool,
    error_class: Optional[str],
    telemetry_sink: Optional[Callable[[Dict[str, Any]], None]],
    start: float,
    network_attempted: bool,
    actual_input_tokens_if_reported: Optional[int] = None,
    actual_output_tokens_if_reported: Optional[int] = None,
    latency_ms: Optional[float] = None,
) -> str:
    preview_metrics = _as_dict(_first(gate, "preview_metrics", default={}))
    event = _build_boundary_telemetry_event(
        event_type=event_type,
        caller_id=str(_first(gate, "caller_id", default="")),
        purpose_code=str(_first(gate, "purpose_code", default="")),
        configured_backend=str(_first(gate, "normalized_backend", default="local")),
        model_id=str(_first(gate, "normalized_model", default="")),
        capability_enabled=bool(cfg.enable_network_semantic_readout),
        authorization_result=str(_first(gate, "authorization_result", default="NOT_REQUESTED")),
        authorization_reason=str(_first(gate, "authorization_reason", default="NOT_REQUESTED")),
        capsule_hash=str(_first(gate, "capsule_hash", default="")),
        projection_hash=_first(gate, "projection_hash", default=None),
        input_bytes=int(_first(preview_metrics, "input_bytes", default=0) or 0),
        estimated_input_tokens=_first(preview_metrics, "estimated_input_tokens", default=None),
        actual_input_tokens_if_reported=actual_input_tokens_if_reported,
        actual_output_tokens_if_reported=actual_output_tokens_if_reported,
        requested_output_limit=int(_first(gate, "requested_output_limit", default=0) or 0),
        latency_ms=latency_ms if latency_ms is not None else (time.perf_counter() - start) * 1000.0,
        network_attempted=network_attempted,
        outcome=outcome,
        fallback_used=fallback_used,
        error_class=error_class,
        retry_count=0,
    )
    if cfg.telemetry_enabled:
        _emit_boundary_telemetry(event, telemetry_sink=telemetry_sink)
    return str(event["event_id"])


def _semantic_readout_authorization_error_class(reason_code: str) -> str:
    reason = str(reason_code or "").strip()
    if reason in {"NOT_REQUESTED", "CAPABILITY_DISABLED", "BACKEND_LOCAL", "BACKEND_NOT_EXPLICIT", "AUTHORIZED"}:
        return "NONE"
    if reason == "CONFIG_INVALID":
        return "CONFIGURATION_ERROR"
    if reason in {"CAPSULE_MISSING", "CAPSULE_INVALID", "CAPSULE_HASH_INVALID"}:
        return "CAPSULE_VALIDATION_ERROR"
    if reason in {
        "MODEL_MISSING",
        "ENDPOINT_NOT_PERMITTED",
        "CREDENTIAL_MISSING",
        "CALLER_MISSING",
        "CALLER_NOT_ALLOWED",
        "PURPOSE_MISSING",
        "PURPOSE_NOT_ALLOWED",
        "BUDGET_EXHAUSTED",
    }:
        return "AUTHORIZATION_DENIAL"
    return "AUTHORIZATION_DENIAL"


def _semantic_readout_local_result(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    cfg: SemanticReadoutConfig,
    gate: Dict[str, Any],
    telemetry_sink: Optional[Callable[[Dict[str, Any]], None]],
    start: float,
    backend_status: str,
    network_attempted: bool,
    emit_boundary_evaluated: bool,
    emit_boundary_denied: bool,
    local_error_class: Optional[str],
    reply_text_override: Optional[str] = None,
    actual_input_tokens_if_reported: Optional[int] = None,
    actual_output_tokens_if_reported: Optional[int] = None,
    summary_id: Optional[str] = None,
) -> Dict[str, Any]:
    reply_text = reply_text_override if reply_text_override is not None else _local_reply(prompt=prompt, runtime_output=runtime_output, cfg=cfg)
    authorization_result = str(_first(gate, "authorization_result", default="NOT_REQUESTED"))
    authorization_reason = str(_first(gate, "authorization_reason", default="NOT_REQUESTED"))
    boundary_error_class = _semantic_readout_authorization_error_class(authorization_reason)
    boundary_fallback = backend_status != "NOT_REQUESTED"
    if emit_boundary_evaluated:
        _emit_semantic_readout_event(
            cfg=cfg,
            gate=gate,
            event_type="BOUNDARY_EVALUATED",
            outcome=authorization_result,
            fallback_used=boundary_fallback,
            error_class=boundary_error_class,
            telemetry_sink=telemetry_sink,
            start=start,
            network_attempted=network_attempted,
        )
    if emit_boundary_denied:
        _emit_semantic_readout_event(
            cfg=cfg,
            gate=gate,
            event_type="BOUNDARY_DENIED",
            outcome="DENIED",
            fallback_used=True,
            error_class=boundary_error_class,
            telemetry_sink=telemetry_sink,
            start=start,
            network_attempted=False,
        )
    local_event_id = _emit_semantic_readout_event(
        cfg=cfg,
        gate=gate,
        event_type="LOCAL_REPLY_RETURNED",
        outcome="LOCAL_REPLY_RETURNED",
        fallback_used=boundary_fallback,
        error_class=local_error_class or boundary_error_class,
        telemetry_sink=telemetry_sink,
        start=start,
        network_attempted=network_attempted,
        actual_input_tokens_if_reported=actual_input_tokens_if_reported,
        actual_output_tokens_if_reported=actual_output_tokens_if_reported,
    )
    return _semantic_readout_reply_record(
        reply_text=reply_text,
        reply_source="LOCAL_DETERMINISTIC",
        backend_status=backend_status,
        authorization_reason=authorization_reason,
        caller_id=str(_first(gate, "caller_id", default="")),
        purpose_code=str(_first(gate, "purpose_code", default="")),
        capsule_hash=str(_first(gate, "capsule_hash", default="")),
        fallback_used=boundary_fallback,
        telemetry_event_id=local_event_id,
        summary_id=summary_id,
    )


def _openai_compatible_reply(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    cfg: SemanticReadoutConfig,
    caller_id: Optional[str] = None,
    purpose_code: Optional[str] = None,
    governed_context_capsule: Optional[Dict[str, Any]] = None,
    telemetry_sink: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    start = time.perf_counter()
    gate = _semantic_readout_capability_gate(
        prompt=prompt,
        runtime_output=runtime_output,
        cfg=cfg,
        caller_id=caller_id,
        purpose_code=purpose_code,
        governed_context_capsule=governed_context_capsule,
    )

    if not bool(_first(gate, "authorized", default=False)):
        return _semantic_readout_local_result(
            prompt=prompt,
            runtime_output=runtime_output,
            cfg=cfg,
            gate=gate,
            telemetry_sink=telemetry_sink,
            start=start,
            backend_status="DENIED" if bool(_first(gate, "network_requested", default=False)) else "NOT_REQUESTED",
            network_attempted=False,
            emit_boundary_evaluated=True,
            emit_boundary_denied=bool(_first(gate, "network_requested", default=False)),
            local_error_class=_semantic_readout_authorization_error_class(str(_first(gate, "authorization_reason", default="NOT_REQUESTED"))),
        )

    _emit_semantic_readout_event(
        cfg=cfg,
        gate=gate,
        event_type="BOUNDARY_EVALUATED",
        outcome="AUTHORIZED",
        fallback_used=False,
        error_class="NONE",
        telemetry_sink=telemetry_sink,
        start=start,
        network_attempted=True,
    )
    _emit_semantic_readout_event(
        cfg=cfg,
        gate=gate,
        event_type="NETWORK_REQUEST_STARTED",
        outcome="AUTHORIZED",
        fallback_used=False,
        error_class="NONE",
        telemetry_sink=telemetry_sink,
        start=start,
        network_attempted=True,
    )

    api_key = os.environ.get("SEMANTIC_READOUT_API_KEY") or os.environ.get("OPENAI_API_KEY")
    payload = dict(_first(gate, "preview_payload", default={}) or {})
    req = urllib.request.Request(
        url=f"{cfg.openai_base_url}/v1/chat/completions",
        data=_stable_json(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=float(cfg.openai_timeout_s)) as resp:
            raw = resp.read()
        data = json.loads(raw.decode("utf-8"))
        choices = data.get("choices", []) if isinstance(data, dict) else []
        usage = data.get("usage", {}) if isinstance(data, dict) else {}
        actual_input_tokens = usage.get("prompt_tokens", None) if isinstance(usage, dict) else None
        actual_output_tokens = usage.get("completion_tokens", None) if isinstance(usage, dict) else None
        content = None
        if choices:
            msg = choices[0].get("message", {}) or {}
            content = msg.get("content", None)
        if isinstance(content, str) and content.strip():
            reply_text = content.strip()
            success_event_id = _emit_semantic_readout_event(
                cfg=cfg,
                gate=gate,
                event_type="NETWORK_REQUEST_SUCCEEDED",
                outcome="SUCCESS",
                fallback_used=False,
                error_class="NONE",
                telemetry_sink=telemetry_sink,
                start=start,
                network_attempted=True,
                actual_input_tokens_if_reported=actual_input_tokens,
                actual_output_tokens_if_reported=actual_output_tokens,
            )
            return _semantic_readout_reply_record(
                reply_text=reply_text,
                reply_source="NETWORK_MODEL",
                backend_status="SUCCESS",
                authorization_reason=str(_first(gate, "authorization_reason", default="AUTHORIZED")),
                caller_id=str(_first(gate, "caller_id", default="")),
                purpose_code=str(_first(gate, "purpose_code", default="")),
                capsule_hash=str(_first(gate, "capsule_hash", default="")),
                fallback_used=False,
                telemetry_event_id=success_event_id,
                summary_id=data.get("id") if isinstance(data, dict) and isinstance(data.get("id"), str) else None,
            )

        failure_class = _classify_semantic_readout_failure(RuntimeError("empty network reply"), content=content, data=data)
        _emit_semantic_readout_event(
            cfg=cfg,
            gate=gate,
            event_type="NETWORK_REQUEST_FAILED",
            outcome="FAILED",
            fallback_used=True,
            error_class=failure_class,
            telemetry_sink=telemetry_sink,
            start=start,
            network_attempted=True,
            actual_input_tokens_if_reported=actual_input_tokens,
            actual_output_tokens_if_reported=actual_output_tokens,
        )
        return _semantic_readout_local_result(
            prompt=prompt,
            runtime_output=runtime_output,
            cfg=cfg,
            gate=gate,
            telemetry_sink=telemetry_sink,
            start=start,
            backend_status="FAILED",
            network_attempted=True,
            emit_boundary_evaluated=False,
            emit_boundary_denied=False,
            local_error_class=failure_class,
            actual_input_tokens_if_reported=actual_input_tokens,
            actual_output_tokens_if_reported=actual_output_tokens,
        )
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, KeyError, OSError) as exc:
        failure_class = _classify_semantic_readout_failure(exc)
        _emit_semantic_readout_event(
            cfg=cfg,
            gate=gate,
            event_type="NETWORK_REQUEST_FAILED",
            outcome="FAILED",
            fallback_used=True,
            error_class=failure_class,
            telemetry_sink=telemetry_sink,
            start=start,
            network_attempted=True,
        )
        return _semantic_readout_local_result(
            prompt=prompt,
            runtime_output=runtime_output,
            cfg=cfg,
            gate=gate,
            telemetry_sink=telemetry_sink,
            start=start,
            backend_status="FAILED",
            network_attempted=True,
            emit_boundary_evaluated=False,
            emit_boundary_denied=False,
            local_error_class=failure_class,
        )


def _local_readout_result(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    cfg: SemanticReadoutConfig,
    caller_id: Optional[str] = None,
    purpose_code: Optional[str] = None,
    governed_context_capsule: Optional[Dict[str, Any]] = None,
    telemetry_sink: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    start = time.perf_counter()
    gate = _semantic_readout_capability_gate(
        prompt=prompt,
        runtime_output=runtime_output,
        cfg=cfg,
        caller_id=caller_id,
        purpose_code=purpose_code,
        governed_context_capsule=governed_context_capsule,
    )
    if not cfg.enabled:
        return _semantic_readout_local_result(
            prompt=prompt,
            runtime_output=runtime_output,
            cfg=cfg,
            gate=gate,
            telemetry_sink=telemetry_sink,
            start=start,
            backend_status="NOT_REQUESTED",
            network_attempted=False,
            emit_boundary_evaluated=True,
            emit_boundary_denied=False,
            local_error_class=None,
            reply_text_override="",
        )
    return _semantic_readout_local_result(
        prompt=prompt,
        runtime_output=runtime_output,
        cfg=cfg,
        gate=gate,
        telemetry_sink=telemetry_sink,
        start=start,
        backend_status="NOT_REQUESTED",
        network_attempted=False,
        emit_boundary_evaluated=True,
        emit_boundary_denied=False,
        local_error_class=None,
    )


def generate_structured_reply(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    caller_id: Optional[str] = None,
    purpose_code: Optional[str] = None,
    governed_context_capsule: Optional[Dict[str, Any]] = None,
    telemetry_sink: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """
    Generate a structured semantic readout result.

    Deterministic local mode remains the default. Optional network mode requires
    explicit capability, caller identity, governed capsule, and permitted backend.
    """
    cfg = _load_cfg(config)
    if not cfg.enabled:
        gate = _semantic_readout_capability_gate(
            prompt=prompt,
            runtime_output=runtime_output,
            cfg=cfg,
            caller_id=caller_id,
            purpose_code=purpose_code,
            governed_context_capsule=governed_context_capsule,
        )
        start = time.perf_counter()
        return _semantic_readout_local_result(
            prompt=prompt,
            runtime_output=runtime_output,
            cfg=cfg,
            gate=gate,
            telemetry_sink=telemetry_sink,
            start=start,
            backend_status="NOT_REQUESTED",
            network_attempted=False,
            emit_boundary_evaluated=True,
            emit_boundary_denied=False,
            local_error_class=None,
            reply_text_override="",
        )

    backend = (cfg.backend or "local").strip().lower()
    if _is_network_backend(backend):
        return _openai_compatible_reply(
            prompt=prompt,
            runtime_output=runtime_output,
            cfg=cfg,
            caller_id=caller_id,
            purpose_code=purpose_code,
            governed_context_capsule=governed_context_capsule,
            telemetry_sink=telemetry_sink,
        )

    return _local_readout_result(
        prompt=prompt,
        runtime_output=runtime_output,
        cfg=cfg,
        caller_id=caller_id,
        purpose_code=purpose_code,
        governed_context_capsule=governed_context_capsule,
        telemetry_sink=telemetry_sink,
    )


def generate_reply(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    caller_id: Optional[str] = None,
    purpose_code: Optional[str] = None,
    governed_context_capsule: Optional[Dict[str, Any]] = None,
    telemetry_sink: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> str:
    """
    Generate a natural-language reply from runtime state.

    Deterministic local mode is the default. Optional LLM backend can be enabled
    via config + environment variables without changing engine behavior.
    """
    result = generate_structured_reply(
        prompt=prompt,
        runtime_output=runtime_output,
        config=config,
        caller_id=caller_id,
        purpose_code=purpose_code,
        governed_context_capsule=governed_context_capsule,
        telemetry_sink=telemetry_sink,
    )
    return str(result.get("reply_text", ""))
