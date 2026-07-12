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
    try:
        return hashlib.sha256(_stable_json(capsule).encode("utf-8")).hexdigest()
    except Exception:
        return ""


def _governed_context_capsule_is_valid(capsule: Any) -> Tuple[bool, str]:
    capsule_dict = _as_dict(capsule)
    if not capsule_dict:
        return False, "missing_governed_context_capsule"

    schema_version = str(_first(capsule_dict, "capsule_schema_version", "schema_version", default="")).strip()
    if schema_version and schema_version != "governed_context_capsule_v1":
        return False, "unsupported_capsule_schema_version"

    missing_sections = [
        section
        for section in _GOVERNED_CAPSULE_REQUIRED_SECTIONS
        if section not in capsule_dict or capsule_dict[section] is None
    ]
    if missing_sections:
        return False, "missing_capsule_sections:" + ",".join(missing_sections)

    return True, "allowed_governed_context_capsule"


def _governed_context_capsule_projection(*, capsule: Dict[str, Any], runtime_output: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    capsule_dict = _as_dict(capsule)
    selected_sections = {
        section: _bounded_projection(capsule_dict[section], depth=2, max_items=8)
        for section in _GOVERNED_CAPSULE_REQUIRED_SECTIONS
        if section in capsule_dict
    }
    return {
        "capsule_id": _capsule_id(capsule_dict),
        "capsule_schema_version": str(
            _first(capsule_dict, "capsule_schema_version", "schema_version", default="governed_context_capsule_v1")
        ),
        "capsule_hash": _capsule_hash(capsule_dict),
        "selected_sections": selected_sections,
        "runtime_summary": _extract_runtime_summary(runtime_output),
        "prompt_summary": {
            "prompt_bytes": len((prompt or "").encode("utf-8")),
            "estimated_prompt_tokens": _approx_token_count(prompt or ""),
        },
    }


def _build_network_request_payload(*, prompt: str, runtime_output: Dict[str, Any], cfg: "SemanticReadoutConfig", capsule_projection: Dict[str, Any]) -> Dict[str, Any]:
    summary = _extract_runtime_summary(runtime_output)
    system = (
        "You are a helpful high-school science tutor. "
        "Answer concisely (2-5 sentences), use simple language, and ask 1 short follow-up question. "
        "If you are uncertain, say so briefly. "
        "Do not mention internal engine implementation unless the user asks."
    )
    user_projection = {
        "prompt": prompt,
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
    caller_id: str,
    backend: str,
    model_id: str,
    capability_enabled: bool,
    authorization_result: str,
    authorization_reason: str,
    capsule_hash: str,
    input_bytes: int,
    estimated_input_tokens: Optional[int],
    actual_input_tokens_if_reported: Optional[int],
    actual_output_tokens_if_reported: Optional[int],
    latency_ms: float,
    outcome: str,
    fallback_used: bool,
    error_class: Optional[str],
) -> Dict[str, Any]:
    return {
        "event_type": "semantic_readout_boundary_v1",
        "event_id": uuid.uuid4().hex,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "caller_id": caller_id,
        "backend": backend,
        "model_id": model_id,
        "capability_enabled": bool(capability_enabled),
        "authorization_result": authorization_result,
        "authorization_reason": authorization_reason,
        "capsule_hash": capsule_hash,
        "input_bytes": int(input_bytes),
        "estimated_input_tokens": estimated_input_tokens,
        "actual_input_tokens_if_reported": actual_input_tokens_if_reported,
        "actual_output_tokens_if_reported": actual_output_tokens_if_reported,
        "latency_ms": float(latency_ms),
        "outcome": outcome,
        "fallback_used": bool(fallback_used),
        "error_class": error_class,
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


def _network_authorization(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    cfg: "SemanticReadoutConfig",
    caller_id: Optional[str],
    governed_context_capsule: Optional[Dict[str, Any]],
) -> Tuple[bool, str, str, str, Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    backend = (cfg.backend or "local").strip().lower()
    capsule_dict = _as_dict(governed_context_capsule)
    capsule_hash = _capsule_hash(capsule_dict) if capsule_dict else ""
    capsule_projection = _governed_context_capsule_projection(capsule=capsule_dict, runtime_output=runtime_output, prompt=prompt) if capsule_dict else {}
    preview_payload = _build_network_request_payload(
        prompt=prompt,
        runtime_output=runtime_output,
        cfg=cfg,
        capsule_projection=capsule_projection,
    )
    preview_payload_bytes = _stable_json(preview_payload).encode("utf-8")
    preview_metrics = {
        "input_bytes": len(preview_payload_bytes),
        "estimated_input_tokens": _approx_token_count(preview_payload),
    }

    if not cfg.enable_network_semantic_readout:
        return False, "DENIED", "capability_disabled", capsule_hash, capsule_projection, preview_payload, preview_metrics
    if not _is_network_backend(backend):
        return False, "DENIED", "backend_not_network", capsule_hash, capsule_projection, preview_payload, preview_metrics
    if not str(cfg.openai_model or "").strip():
        return False, "DENIED", "missing_model_id", capsule_hash, capsule_projection, preview_payload, preview_metrics
    if _normalize_endpoint(cfg.openai_base_url) not in _normalize_endpoint_list(cfg.allowed_network_endpoints):
        return False, "DENIED", "endpoint_not_permitted", capsule_hash, capsule_projection, preview_payload, preview_metrics
    if not (os.environ.get("SEMANTIC_READOUT_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        return False, "DENIED", "missing_credential", capsule_hash, capsule_projection, preview_payload, preview_metrics
    if not str(caller_id or "").strip():
        return False, "DENIED", "missing_caller_identity", capsule_hash, capsule_projection, preview_payload, preview_metrics

    valid_capsule, capsule_reason = _governed_context_capsule_is_valid(capsule_dict)
    if not valid_capsule:
        return False, "DENIED", capsule_reason, capsule_hash, capsule_projection, preview_payload, preview_metrics

    return True, "ALLOWED", "allowed", capsule_hash, capsule_projection, preview_payload, preview_metrics


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


def _openai_compatible_reply(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    cfg: SemanticReadoutConfig,
    caller_id: Optional[str] = None,
    governed_context_capsule: Optional[Dict[str, Any]] = None,
    telemetry_sink: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    start = time.perf_counter()
    (
        authorized,
        authorization_result,
        authorization_reason,
        capsule_hash,
        capsule_projection,
        preview_payload,
        preview_metrics,
    ) = _network_authorization(
        prompt=prompt,
        runtime_output=runtime_output,
        cfg=cfg,
        caller_id=caller_id,
        governed_context_capsule=governed_context_capsule,
    )

    if not authorized:
        reply_text = _local_reply(prompt=prompt, runtime_output=runtime_output, cfg=cfg)
        event = _build_boundary_telemetry_event(
            caller_id=str(caller_id or ""),
            backend=(cfg.backend or "local").strip().lower(),
            model_id=str(cfg.openai_model or ""),
            capability_enabled=bool(cfg.enable_network_semantic_readout),
            authorization_result=authorization_result,
            authorization_reason=authorization_reason,
            capsule_hash=capsule_hash,
            input_bytes=int(preview_metrics["input_bytes"]),
            estimated_input_tokens=int(preview_metrics["estimated_input_tokens"]),
            actual_input_tokens_if_reported=None,
            actual_output_tokens_if_reported=None,
            latency_ms=(time.perf_counter() - start) * 1000.0,
            outcome="DENIED",
            fallback_used=True,
            error_class=authorization_reason,
        )
        _emit_boundary_telemetry(event, telemetry_sink=telemetry_sink)
        return {
            "reply_text": reply_text,
            "reply_source": "LOCAL_DETERMINISTIC",
            "summary_id": None,
            "capsule_hash": capsule_hash,
            "backend_status": "DENIED",
            "fallback_used": True,
        }

    api_key = os.environ.get("SEMANTIC_READOUT_API_KEY") or os.environ.get("OPENAI_API_KEY")
    payload = preview_payload
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
        reply_text = content.strip() if isinstance(content, str) and content.strip() else _local_reply(prompt=prompt, runtime_output=runtime_output, cfg=cfg)
        backend_status = "SUCCESS" if isinstance(content, str) and content.strip() else "FAILED"
        reply_source = "NETWORK_MODEL" if backend_status == "SUCCESS" else "LOCAL_DETERMINISTIC"
        event = _build_boundary_telemetry_event(
            caller_id=str(caller_id or ""),
            backend=(cfg.backend or "local").strip().lower(),
            model_id=str(cfg.openai_model or ""),
            capability_enabled=bool(cfg.enable_network_semantic_readout),
            authorization_result=authorization_result,
            authorization_reason=authorization_reason,
            capsule_hash=capsule_hash,
            input_bytes=int(preview_metrics["input_bytes"]),
            estimated_input_tokens=int(preview_metrics["estimated_input_tokens"]),
            actual_input_tokens_if_reported=actual_input_tokens,
            actual_output_tokens_if_reported=actual_output_tokens,
            latency_ms=(time.perf_counter() - start) * 1000.0,
            outcome=backend_status,
            fallback_used=(backend_status != "SUCCESS"),
            error_class=None if backend_status == "SUCCESS" else "empty_network_reply",
        )
        _emit_boundary_telemetry(event, telemetry_sink=telemetry_sink)
        return {
            "reply_text": reply_text,
            "reply_source": reply_source,
            "summary_id": data.get("id") if isinstance(data, dict) and isinstance(data.get("id"), str) else None,
            "capsule_hash": capsule_hash,
            "backend_status": backend_status,
            "fallback_used": backend_status != "SUCCESS",
        }
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, OSError) as exc:
        reply_text = _local_reply(prompt=prompt, runtime_output=runtime_output, cfg=cfg)
        event = _build_boundary_telemetry_event(
            caller_id=str(caller_id or ""),
            backend=(cfg.backend or "local").strip().lower(),
            model_id=str(cfg.openai_model or ""),
            capability_enabled=bool(cfg.enable_network_semantic_readout),
            authorization_result=authorization_result,
            authorization_reason=authorization_reason,
            capsule_hash=capsule_hash,
            input_bytes=int(preview_metrics["input_bytes"]),
            estimated_input_tokens=int(preview_metrics["estimated_input_tokens"]),
            actual_input_tokens_if_reported=None,
            actual_output_tokens_if_reported=None,
            latency_ms=(time.perf_counter() - start) * 1000.0,
            outcome="FAILED",
            fallback_used=True,
            error_class=exc.__class__.__name__,
        )
        _emit_boundary_telemetry(event, telemetry_sink=telemetry_sink)
        return {
            "reply_text": reply_text,
            "reply_source": "LOCAL_DETERMINISTIC",
            "summary_id": None,
            "capsule_hash": capsule_hash,
            "backend_status": "FAILED",
            "fallback_used": True,
        }


def _local_readout_result(*, prompt: str, runtime_output: Dict[str, Any], cfg: SemanticReadoutConfig) -> Dict[str, Any]:
    return {
        "reply_text": _local_reply(prompt=prompt, runtime_output=runtime_output, cfg=cfg),
        "reply_source": "LOCAL_DETERMINISTIC",
        "summary_id": None,
        "capsule_hash": "",
        "backend_status": "NOT_REQUESTED",
        "fallback_used": False,
    }


def generate_structured_reply(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    caller_id: Optional[str] = None,
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
        return {
            "reply_text": "",
            "reply_source": "LOCAL_DETERMINISTIC",
            "summary_id": None,
            "capsule_hash": "",
            "backend_status": "NOT_REQUESTED",
            "fallback_used": False,
        }

    backend = (cfg.backend or "local").strip().lower()
    if _is_network_backend(backend):
        return _openai_compatible_reply(
            prompt=prompt,
            runtime_output=runtime_output,
            cfg=cfg,
            caller_id=caller_id,
            governed_context_capsule=governed_context_capsule,
            telemetry_sink=telemetry_sink,
        )

    return _local_readout_result(prompt=prompt, runtime_output=runtime_output, cfg=cfg)


def generate_reply(
    *,
    prompt: str,
    runtime_output: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    caller_id: Optional[str] = None,
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
        governed_context_capsule=governed_context_capsule,
        telemetry_sink=telemetry_sink,
    )
    return str(result.get("reply_text", ""))
