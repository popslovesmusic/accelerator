from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from .cache_policy import (
    CACHE_NAMESPACE_DEFAULT,
    DEFAULT_BOUNDARY_POLICY_VERSION,
    DEFAULT_DETERMINISTIC_METHOD_VERSION,
    DEFAULT_RESULT_SCHEMA_ID,
    DEFAULT_OUTPUT_SCHEMA_VERSION,
    DEFAULT_VALIDATOR_VERSION,
    build_cache_key_materialized_record,
    build_request_semantics_v1,
    hash_json_value,
    normalize_identifier_list,
    normalize_string,
    normalize_tree,
)


def _prompt_signature(prompt: str) -> str:
    normalized_prompt = " ".join(str(prompt or "").replace("\r", " ").replace("\n", " ").split())
    return hashlib.sha256(normalized_prompt.encode("utf-8")).hexdigest()


def _runtime_signature(runtime_output: Mapping[str, Any]) -> Dict[str, Any]:
    state = dict(runtime_output.get("state", {}) or {})
    signature = dict(state.get("signature", {}) or {})
    orientation = dict(state.get("orientation", {}) or {})
    reasoning = dict(state.get("reasoning", {}) or {})
    output = dict(runtime_output.get("output", {}) or {})
    return {
        "state_signature": {
            "active_component_id": signature.get("active_component_id"),
            "caution_scalar": signature.get("caution_scalar"),
            "raw_caution_scalar": signature.get("raw_caution_scalar"),
            "recovery_scalar": signature.get("recovery_scalar"),
            "hold_state": signature.get("hold_state"),
            "components": normalize_identifier_list(signature.get("components", [])),
        },
        "orientation": {"active_operator": orientation.get("active_operator")},
        "reasoning": {"hold_semantics": reasoning.get("hold_semantics")},
        "output": {
            "selected_class": output.get("selected_class"),
            "confidence": output.get("confidence"),
        },
    }


def build_runtime_signature_hash(runtime_output: Mapping[str, Any]) -> str:
    return hash_json_value(_runtime_signature(runtime_output))


def build_configuration_signature(config: Mapping[str, Any]) -> Dict[str, Any]:
    cfg = dict(config or {})
    sr = dict(cfg.get("semantic_readout", {}) or {})
    oc = dict(sr.get("openai_compatible", sr.get("openai", {})) or {})
    return {
        "semantic_readout": {
            "enabled": bool(sr.get("enabled", True)),
            "backend": normalize_string(sr.get("backend", "local"), lowercase=True),
            "style": normalize_string(sr.get("style", "hs_science")),
            "max_sentences": int(sr.get("max_sentences", 4) or 4),
            "include_followup_question": bool(sr.get("include_followup_question", True)),
            "caution_hedge_threshold": float(sr.get("caution_hedge_threshold", 0.65) or 0.65),
            "hold_explain": bool(sr.get("hold_explain", True)),
            "openai_compatible": {
                "base_url": normalize_string(oc.get("base_url", "https://api.openai.com")).rstrip("/"),
                "model": normalize_string(oc.get("model", "")),
                "timeout_s": float(oc.get("timeout_s", 12.0) or 12.0),
            },
            "enable_network_semantic_readout": bool(sr.get("enable_network_semantic_readout", False)),
            "allowed_network_endpoints": normalize_identifier_list(sr.get("allowed_network_endpoints", [])),
            "network_retry_budget": int(sr.get("network_retry_budget", sr.get("retry_budget", 0)) or 0),
            "allowed_callers": normalize_identifier_list(sr.get("allowed_callers", [])),
            "allowed_purposes": normalize_identifier_list(sr.get("allowed_purposes", [])),
            "telemetry_enabled": bool(sr.get("telemetry_enabled", True)),
            "log_prompt_content": bool(sr.get("log_prompt_content", False)),
        },
    }


def build_configuration_hash(config: Mapping[str, Any]) -> str:
    return hash_json_value(build_configuration_signature(config))


def build_repository_snapshot_hash(paths: Sequence[str | Path]) -> str:
    file_hashes: Dict[str, Any] = {}
    for path in paths or []:
        file_path = Path(path)
        try:
            if file_path.exists() and file_path.is_file():
                file_hashes[str(file_path.as_posix())] = hashlib.sha256(file_path.read_bytes()).hexdigest()
            else:
                file_hashes[str(file_path.as_posix())] = None
        except OSError:
            file_hashes[str(file_path.as_posix())] = None
    return hash_json_value(file_hashes)


def build_semantic_readout_request_semantics(
    *,
    prompt: str,
    runtime_output: Mapping[str, Any],
    config: Mapping[str, Any],
    caller_id: str,
    purpose_code: str,
    governed_context_capsule: Mapping[str, Any],
    candidate_ids: Sequence[Any],
    requested_output_type: str,
    decision_type: str,
    cache_namespace: str,
) -> Dict[str, Any]:
    capsule_dict = dict(governed_context_capsule or {})
    runtime_signature = _runtime_signature(runtime_output)
    capsule_projection = dict(capsule_dict.get("runtime", {}) or {})
    prompt_signature = _prompt_signature(prompt)
    configuration_signature = build_configuration_signature(config)
    constraints = {
        "caller_id": normalize_string(caller_id),
        "purpose_code": normalize_string(purpose_code),
        "prompt_signature": prompt_signature,
        "prompt_token_count": max(1, (len(str(prompt or "").encode("utf-8")) + 3) // 4) if prompt else 0,
        "runtime_signature_hash": hash_json_value(runtime_signature),
        "capsule_projection_hash": hash_json_value(capsule_projection),
        "configuration_hash": hash_json_value(configuration_signature),
        "log_prompt_content": bool(configuration_signature["semantic_readout"]["log_prompt_content"]),
        "backend": normalize_string(configuration_signature["semantic_readout"]["backend"], lowercase=True),
        "model_id": normalize_string(configuration_signature["semantic_readout"]["openai_compatible"]["model"]),
        "style": normalize_string(configuration_signature["semantic_readout"]["style"]),
        "max_sentences": int(configuration_signature["semantic_readout"]["max_sentences"]),
        "include_followup_question": bool(configuration_signature["semantic_readout"]["include_followup_question"]),
        "hold_explain": bool(configuration_signature["semantic_readout"]["hold_explain"]),
    }
    return build_request_semantics_v1(
        operation="semantic_readout.generate_structured_reply",
        target_scope={
            "boundary_id": "SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
            "capsule_hash": normalize_string(capsule_dict.get("capsule_hash")),
            "capsule_projection_hash": hash_json_value(capsule_projection),
            "runtime_signature_hash": hash_json_value(runtime_signature),
        },
        requested_output_type=requested_output_type,
        constraints=constraints,
        candidate_ids=candidate_ids,
        exclusions=("raw_prompt_text", "raw_model_prose", "secret_material", "unvalidated_output"),
        diagnostic_metadata={
            "prompt_length": len(str(prompt or "")),
            "prompt_signature": prompt_signature,
            "caller_id": normalize_string(caller_id),
            "purpose_code": normalize_string(purpose_code),
        },
        boundary_id="SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
        purpose_code=purpose_code,
        authority_class="PRESENTATION_ONLY",
        cache_namespace=cache_namespace,
        decision_type=decision_type,
    )


def build_semantic_readout_cache_context(
    *,
    prompt: str,
    runtime_output: Mapping[str, Any],
    config: Mapping[str, Any],
    caller_id: str,
    purpose_code: str,
    governed_context_capsule: Mapping[str, Any],
    candidate_ids: Sequence[Any],
    decision_type: str,
    cache_namespace: str = CACHE_NAMESPACE_DEFAULT,
    boundary_policy_version: str = DEFAULT_BOUNDARY_POLICY_VERSION,
    deterministic_method_version: str = DEFAULT_DETERMINISTIC_METHOD_VERSION,
    validator_version: str = DEFAULT_VALIDATOR_VERSION,
    output_schema_version: str = DEFAULT_OUTPUT_SCHEMA_VERSION,
    requested_output_type: str = DEFAULT_RESULT_SCHEMA_ID,
    tool_registry_hash: str | None = None,
    repository_snapshot_paths: Sequence[str | Path] | None = None,
    caller_policy_class: str = "PRESENTATION_ONLY",
) -> Dict[str, Any]:
    capsule_dict = dict(governed_context_capsule or {})
    runtime_signature = _runtime_signature(runtime_output)
    configuration_signature = build_configuration_signature(config)
    allowed_callers = normalize_identifier_list(
        configuration_signature["semantic_readout"]["allowed_callers"]
    )
    allowed_purposes = normalize_identifier_list(
        configuration_signature["semantic_readout"]["allowed_purposes"]
    )
    backend = normalize_string(
        configuration_signature["semantic_readout"]["backend"],
        lowercase=True,
    )
    model_id = normalize_string(
        configuration_signature["semantic_readout"]["openai_compatible"]["model"]
    )
    request_semantics = build_semantic_readout_request_semantics(
        prompt=prompt,
        runtime_output=runtime_output,
        config=config,
        caller_id=caller_id,
        purpose_code=purpose_code,
        governed_context_capsule=governed_context_capsule,
        candidate_ids=candidate_ids,
        requested_output_type=requested_output_type,
        decision_type=decision_type,
        cache_namespace=cache_namespace,
    )
    request_semantics_hash = hash_json_value(request_semantics)
    candidate_ids_normalized = normalize_identifier_list(candidate_ids)
    candidate_set_hash = hash_json_value(candidate_ids_normalized)
    authority_hash = hash_json_value(
        {
            "caller_id": normalize_string(caller_id),
            "purpose_code": normalize_string(purpose_code),
            "caller_policy_class": normalize_string(caller_policy_class, uppercase=True),
            "authority": normalize_tree(capsule_dict.get("authority", {})),
            "boundary_id": "SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
            "backend": backend,
            "enable_network_semantic_readout": bool(configuration_signature["semantic_readout"]["enable_network_semantic_readout"]),
            "allowed_callers": allowed_callers,
            "allowed_purposes": allowed_purposes,
            "model_id": model_id,
        }
    )
    freshness_hash = hash_json_value(
        {
            "freshness": normalize_tree(capsule_dict.get("freshness", {})),
            "current_state": normalize_tree(capsule_dict.get("current_state", {})),
            "runtime_signature_hash": hash_json_value(runtime_signature),
        }
    )
    repository_snapshot_hash = build_repository_snapshot_hash(repository_snapshot_paths or [])
    configuration_hash = hash_json_value(configuration_signature)
    cache_key_record = build_cache_key_materialized_record(
        cache_namespace=cache_namespace,
        decision_type=decision_type,
        request_semantics=request_semantics,
        capsule_hash=normalize_string(capsule_dict.get("capsule_hash")),
        authority_hash=authority_hash,
        freshness_hash=freshness_hash,
        boundary_id="SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
        boundary_policy_version=boundary_policy_version,
        purpose_code=purpose_code,
        caller_policy_class=caller_policy_class,
        candidate_set_hash=candidate_set_hash,
        deterministic_method_version=deterministic_method_version,
        validator_version=validator_version,
        output_schema_version=output_schema_version,
        tool_registry_hash=tool_registry_hash,
        repository_snapshot_hash=repository_snapshot_hash,
        runtime_signature_hash=hash_json_value(runtime_signature),
        configuration_hash=configuration_hash,
    )
    return {
        "cache_namespace": cache_namespace,
        "decision_type": decision_type,
        "request_semantics": cache_key_record["request_semantics"],
        "request_semantics_hash": cache_key_record["request_semantics_hash"],
        "cache_key": cache_key_record["cache_key"],
        "cache_key_payload": cache_key_record["cache_key_payload"],
        "boundary_id": "SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
        "boundary_policy_version": boundary_policy_version,
        "purpose_code": purpose_code,
        "caller_policy_class": caller_policy_class,
        "candidate_ids": candidate_ids_normalized,
        "candidate_set_hash": candidate_set_hash,
        "capsule_hash": normalize_string(capsule_dict.get("capsule_hash")),
        "authority_hash": authority_hash,
        "freshness_hash": freshness_hash,
        "deterministic_method_version": deterministic_method_version,
        "validator_version": validator_version,
        "output_schema_version": output_schema_version,
        "tool_registry_hash": tool_registry_hash,
        "repository_snapshot_hash": repository_snapshot_hash,
        "runtime_signature_hash": hash_json_value(runtime_signature),
        "configuration_hash": configuration_hash,
        "invalidation_dependencies": {
            "capsule_hash": normalize_string(capsule_dict.get("capsule_hash")),
            "authority_hash": authority_hash,
            "freshness_hash": freshness_hash,
            "boundary_id": "SEMANTIC_READOUT_OPTIONAL_OPENAI_001",
            "boundary_policy_version": boundary_policy_version,
            "deterministic_method_version": deterministic_method_version,
            "validator_version": validator_version,
            "output_schema_version": output_schema_version,
            "candidate_set_hash": candidate_set_hash,
            "request_semantics_hash": cache_key_record["request_semantics_hash"],
            "tool_registry_hash": tool_registry_hash,
            "repository_snapshot_hash": repository_snapshot_hash,
            "runtime_signature_hash": hash_json_value(runtime_signature),
            "configuration_hash": configuration_hash,
        },
    }
