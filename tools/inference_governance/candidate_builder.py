from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Sequence

from .candidate_policy import (
    BOUND_CANDIDATE_SET_SCHEMA_ID,
    BOUND_CANDIDATE_SET_SCHEMA_VERSION,
    DEFAULT_CANDIDATE_LIMIT,
    DEFAULT_EMPTY_SET_BEHAVIOR,
    DEFAULT_RANKING_METHOD,
    get_candidate_policy,
    hash_candidate_universe,
)
from .request_normalization import hash_json_value, normalize_identifier, normalize_identifier_list, normalize_text, normalize_tree


_ELIGIBLE_STATUSES = {
    "ELIGIBLE",
    "ACCEPTED",
    "ACTIVE",
    "APPROVED",
    "IN_SCOPE",
    "SELECTED",
    "AVAILABLE",
}
_ELIGIBLE_INCOMPATIBLE_STATUSES = {
    "DENIED",
    "DISABLED",
    "DEPRECATED",
    "INCOMPATIBLE",
    "STALE",
    "OUT_OF_SCOPE",
    "MISSING_DEPENDENCY",
    "WRONG_TYPE",
    "POLICY_EXCLUDED",
}

_EXCLUSION_REASON_FOR_STATUS = {
    "DENIED": "AUTHORITY_DENIED",
    "DISABLED": "DISABLED",
    "DEPRECATED": "DEPRECATED",
    "INCOMPATIBLE": "INCOMPATIBLE",
    "STALE": "STALE",
    "OUT_OF_SCOPE": "OUT_OF_SCOPE",
    "MISSING_DEPENDENCY": "MISSING_DEPENDENCY",
    "WRONG_TYPE": "WRONG_TYPE",
    "POLICY_EXCLUDED": "POLICY_EXCLUDED",
}


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    candidate_dict = dict(candidate or {})
    for key in ("candidate_id", "id", "name", "label", "path", "operation_code", "handler_id", "schema_id", "tool_name", "action_id"):
        text = normalize_text(candidate_dict.get(key))
        if text:
            return text
    return normalize_text(candidate_dict)


def _canonical_name(candidate: Mapping[str, Any], candidate_id: str) -> str:
    candidate_dict = dict(candidate or {})
    for key in ("canonical_name", "name", "label", "path", "operation_code", "handler_id", "schema_id", "tool_name", "action_id"):
        text = normalize_text(candidate_dict.get(key))
        if text:
            return text
    return candidate_id


def _rank_score(candidate: Mapping[str, Any]) -> float:
    candidate_dict = dict(candidate or {})
    for key in ("rank_score", "score", "priority_score"):
        value = candidate_dict.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except Exception:
            continue
    return 0.0


def _normalize_status(value: Any) -> str:
    return normalize_text(value, uppercase=True)


def normalize_candidate_record(candidate: Mapping[str, Any], *, candidate_type: str) -> Dict[str, Any]:
    candidate_dict = dict(candidate or {})
    candidate_id = _candidate_id(candidate_dict)
    canonical_name = _canonical_name(candidate_dict, candidate_id)
    rank_components = candidate_dict.get("rank_components")
    if rank_components is None:
        rank_components = candidate_dict.get("rank_breakdown")
    provenance = candidate_dict.get("provenance")
    if provenance is None:
        provenance = {
            "source": normalize_text(candidate_dict.get("source")),
            "policy_rule_id": normalize_text(candidate_dict.get("policy_rule_id")),
        }
    normalized = {
        "candidate_type": normalize_text(candidate_dict.get("candidate_type") or candidate_type, uppercase=True),
        "candidate_id": candidate_id,
        "canonical_name": canonical_name,
        "eligibility_status": _normalize_status(candidate_dict.get("eligibility_status") or candidate_dict.get("status")),
        "authority_status": _normalize_status(candidate_dict.get("authority_status") or candidate_dict.get("authority")),
        "freshness_status": _normalize_status(candidate_dict.get("freshness_status") or candidate_dict.get("freshness")),
        "compatibility_status": _normalize_status(candidate_dict.get("compatibility_status") or candidate_dict.get("compatibility")),
        "rank_score": _rank_score(candidate_dict),
        "rank_components": normalize_tree(rank_components or {}),
        "provenance": normalize_tree(provenance or {}),
    }
    exclusion_reason = candidate_dict.get("exclusion_reason")
    if exclusion_reason is not None:
        normalized["exclusion_reason"] = normalize_text(exclusion_reason, uppercase=True)
    policy_rule_id = candidate_dict.get("policy_rule_id")
    if policy_rule_id is not None:
        normalized["policy_rule_id"] = normalize_text(policy_rule_id)
    return normalized


def _is_eligible(candidate: Mapping[str, Any]) -> bool:
    status = normalize_text(candidate.get("eligibility_status"), uppercase=True)
    if not status:
        return True
    if status in _ELIGIBLE_STATUSES:
        return True
    if status in _ELIGIBLE_INCOMPATIBLE_STATUSES:
        return False
    return True


def _exclusion_reason(candidate: Mapping[str, Any], *, reason_override: str | None = None) -> str:
    if reason_override:
        return normalize_text(reason_override, uppercase=True)
    status = normalize_text(candidate.get("eligibility_status"), uppercase=True)
    if status in _EXCLUSION_REASON_FOR_STATUS:
        return _EXCLUSION_REASON_FOR_STATUS[status]
    if not status:
        return "POLICY_EXCLUDED"
    return status


def _candidate_sort_key(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    try:
        rank_score = float(candidate.get("rank_score", 0.0) or 0.0)
    except Exception:
        rank_score = 0.0
    return (-rank_score, normalize_text(candidate.get("candidate_id")), normalize_text(candidate.get("canonical_name")))


def _candidate_summary(candidate: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "candidate_id": normalize_text(candidate.get("candidate_id")),
        "canonical_name": normalize_text(candidate.get("canonical_name")),
        "eligibility_status": _normalize_status(candidate.get("eligibility_status")),
        "authority_status": _normalize_status(candidate.get("authority_status")),
        "freshness_status": _normalize_status(candidate.get("freshness_status")),
        "compatibility_status": _normalize_status(candidate.get("compatibility_status")),
        "rank_score": float(candidate.get("rank_score", 0.0) or 0.0),
        "rank_components": normalize_tree(candidate.get("rank_components") or {}),
        "provenance": normalize_tree(candidate.get("provenance") or {}),
    }


def build_bounded_candidate_set_v1(
    *,
    candidate_type: str,
    candidate_policy: Mapping[str, Any] | None,
    universe_candidates: Sequence[Mapping[str, Any]],
    authority_hash: str,
    freshness_hash: str,
    universe_hash: str | None = None,
    operation_code: str | None = None,
    candidate_policy_id: str | None = None,
    candidate_policy_version: str | None = None,
) -> Dict[str, Any]:
    policy = dict(candidate_policy or {})
    policy_id = normalize_text(candidate_policy_id or policy.get("candidate_policy_id"), lowercase=True)
    candidate_type_name = normalize_text(candidate_type, uppercase=True)
    policy_version = normalize_text(candidate_policy_version or policy.get("policy_version") or policy.get("candidate_policy_version") or "1.0.0")
    maximum_candidates = policy.get("maximum_candidates", DEFAULT_CANDIDATE_LIMIT)
    try:
        maximum_candidates = max(0, int(maximum_candidates or DEFAULT_CANDIDATE_LIMIT))
    except Exception:
        maximum_candidates = DEFAULT_CANDIDATE_LIMIT
    ranking_method = normalize_text(policy.get("ranking_method"), lowercase=True) or DEFAULT_RANKING_METHOD
    tie_behavior = normalize_text(policy.get("tie_behavior"), lowercase=True) or "candidate_id"
    empty_set_behavior = normalize_text(policy.get("empty_set_behavior")) or DEFAULT_EMPTY_SET_BEHAVIOR
    universe_candidates_normalized = [
        normalize_candidate_record(candidate, candidate_type=candidate_type_name)
        for candidate in universe_candidates or []
        if isinstance(candidate, dict)
    ]
    if universe_hash is None:
        universe_hash = hash_candidate_universe(
            universe_candidates_normalized,
            candidate_type=candidate_type_name,
            candidate_policy_id=policy_id,
            policy_version=policy_version,
        )

    sorted_universe = sorted(universe_candidates_normalized, key=_candidate_sort_key)
    eligible_candidates: list[Dict[str, Any]] = []
    excluded_candidates: list[Dict[str, Any]] = []
    seen_candidate_ids: set[str] = set()

    for candidate in sorted_universe:
        candidate_id = normalize_text(candidate.get("candidate_id"))
        if not candidate_id:
            continue
        if candidate_id in seen_candidate_ids:
            excluded_candidates.append(
                {
                    "candidate_id": candidate_id,
                    "reason_code": "DUPLICATE_ALIAS",
                    "policy_rule_id": f"{policy_id}:dedupe",
                }
            )
            continue
        seen_candidate_ids.add(candidate_id)
        if not _is_eligible(candidate):
            excluded_candidates.append(
                {
                    "candidate_id": candidate_id,
                    "reason_code": _exclusion_reason(candidate),
                    "policy_rule_id": normalize_text(candidate.get("policy_rule_id")) or f"{policy_id}:eligibility",
                }
            )
            continue
        eligible_candidates.append(candidate)

    pruned_candidates = eligible_candidates[:maximum_candidates]
    if len(eligible_candidates) > maximum_candidates:
        for candidate in eligible_candidates[maximum_candidates:]:
            excluded_candidates.append(
                {
                    "candidate_id": normalize_text(candidate.get("candidate_id")),
                    "reason_code": "CANDIDATE_LIMIT_PRUNED",
                    "policy_rule_id": f"{policy_id}:maximum_candidates",
                }
            )

    eligible_summary = [_candidate_summary(candidate) for candidate in pruned_candidates]
    excluded_summary = [
        {
            "candidate_id": normalize_text(candidate.get("candidate_id")),
            "reason_code": normalize_text(candidate.get("reason_code"), uppercase=True),
            "policy_rule_id": normalize_text(candidate.get("policy_rule_id")),
        }
        for candidate in excluded_candidates
    ]
    candidate_set_hash_basis = {
        "candidate_type": candidate_type_name,
        "candidate_policy_id": policy_id,
        "candidate_policy_version": policy_version,
        "operation_code": normalize_text(operation_code, lowercase=True),
        "universe_hash": normalize_text(universe_hash),
        "authority_hash": normalize_text(authority_hash),
        "freshness_hash": normalize_text(freshness_hash),
        "eligible_candidates": [
            {
                "candidate_id": item["candidate_id"],
                "eligibility_status": item["eligibility_status"],
                "authority_status": item["authority_status"],
                "freshness_status": item["freshness_status"],
                "compatibility_status": item["compatibility_status"],
            }
            for item in eligible_summary
        ],
        "excluded_candidates": excluded_summary,
    }
    candidate_set_hash = hash_json_value(candidate_set_hash_basis)
    candidate_set = {
        "schema_id": BOUND_CANDIDATE_SET_SCHEMA_ID,
        "schema_version": BOUND_CANDIDATE_SET_SCHEMA_VERSION,
        "candidate_type": candidate_type_name,
        "candidate_policy_id": policy_id,
        "candidate_policy_version": policy_version,
        "operation_code": normalize_text(operation_code, lowercase=True),
        "universe_source": normalize_text(policy.get("universe_source")),
        "universe_hash": normalize_text(universe_hash),
        "eligible_candidates": eligible_summary,
        "excluded_candidates": excluded_summary,
        "candidate_set_hash": candidate_set_hash,
        "ranking_record": {
            "ranking_method": ranking_method,
            "tie_behavior": tie_behavior,
            "maximum_candidates": maximum_candidates,
            "ordered_candidate_ids": [item["candidate_id"] for item in eligible_summary],
            "empty_set_behavior": empty_set_behavior,
        },
        "authority_hash": normalize_text(authority_hash),
        "freshness_hash": normalize_text(freshness_hash),
        "policy_version": policy_version,
        "candidate_count": len(eligible_summary),
        "excluded_count": len(excluded_summary),
        "maximum_candidates": maximum_candidates,
        "empty_set_behavior": empty_set_behavior,
    }
    candidate_set["resolution"] = resolve_candidate_set_v1(candidate_set)
    return candidate_set


def build_candidate_set_hash(candidate_set: Mapping[str, Any]) -> str:
    return hash_json_value(
        {
            "candidate_type": normalize_text(candidate_set.get("candidate_type"), uppercase=True),
            "candidate_policy_id": normalize_text(candidate_set.get("candidate_policy_id"), lowercase=True),
            "candidate_policy_version": normalize_text(candidate_set.get("candidate_policy_version")),
            "operation_code": normalize_text(candidate_set.get("operation_code"), lowercase=True),
            "universe_hash": normalize_text(candidate_set.get("universe_hash")),
            "authority_hash": normalize_text(candidate_set.get("authority_hash")),
            "freshness_hash": normalize_text(candidate_set.get("freshness_hash")),
            "eligible_candidates": [
                {
                    "candidate_id": normalize_text(candidate.get("candidate_id")),
                    "eligibility_status": normalize_text(candidate.get("eligibility_status"), uppercase=True),
                    "authority_status": normalize_text(candidate.get("authority_status"), uppercase=True),
                    "freshness_status": normalize_text(candidate.get("freshness_status"), uppercase=True),
                    "compatibility_status": normalize_text(candidate.get("compatibility_status"), uppercase=True),
                }
                for candidate in candidate_set.get("eligible_candidates", [])
                if isinstance(candidate, dict)
            ],
            "excluded_candidates": [
                {
                    "candidate_id": normalize_text(candidate.get("candidate_id")),
                    "reason_code": normalize_text(candidate.get("reason_code"), uppercase=True),
                    "policy_rule_id": normalize_text(candidate.get("policy_rule_id")),
                }
                for candidate in candidate_set.get("excluded_candidates", [])
                if isinstance(candidate, dict)
            ],
        }
    )


def resolve_candidate_set_v1(candidate_set: Mapping[str, Any], requested_candidate_id: str | None = None) -> Dict[str, Any]:
    candidate_set_dict = dict(candidate_set or {})
    eligible_candidates = [dict(candidate) for candidate in candidate_set_dict.get("eligible_candidates", []) if isinstance(candidate, dict)]
    eligible_candidate_ids = [
        normalize_text(candidate.get("candidate_id"))
        for candidate in eligible_candidates
        if normalize_text(candidate.get("candidate_id"))
    ]
    requested_id = normalize_text(requested_candidate_id)
    selected_candidate = eligible_candidates[0] if eligible_candidates else None
    selected_candidate_id = normalize_text(selected_candidate.get("candidate_id")) if selected_candidate else ""
    strict_dominance = False
    if len(eligible_candidates) > 1:
        try:
            strict_dominance = float(eligible_candidates[0].get("rank_score", 0.0) or 0.0) > float(
                eligible_candidates[1].get("rank_score", 0.0) or 0.0
            )
        except Exception:
            strict_dominance = False

    if requested_id and requested_id not in eligible_candidate_ids:
        return {
            "resolution_status": "CANDIDATE_OUT_OF_SET",
            "reason_code": "OUT_OF_SET",
            "candidate_count": len(eligible_candidates),
            "eligible_candidate_ids": eligible_candidate_ids,
            "requested_candidate_id": requested_id,
            "selected_candidate_id": "",
            "selected_candidate": None,
            "strict_dominance": False,
        }

    if not eligible_candidates:
        return {
            "resolution_status": "DETERMINISTIC_NO_CANDIDATE",
            "reason_code": "NO_ELIGIBLE_CANDIDATES",
            "candidate_count": 0,
            "eligible_candidate_ids": [],
            "requested_candidate_id": requested_id,
            "selected_candidate_id": "",
            "selected_candidate": None,
            "strict_dominance": False,
        }

    if len(eligible_candidates) == 1:
        return {
            "resolution_status": "DETERMINISTIC_SINGLE_CANDIDATE",
            "reason_code": "SINGLE_ELIGIBLE_CANDIDATE",
            "candidate_count": 1,
            "eligible_candidate_ids": eligible_candidate_ids,
            "requested_candidate_id": requested_id,
            "selected_candidate_id": selected_candidate_id,
            "selected_candidate": _candidate_summary(selected_candidate),
            "strict_dominance": True,
        }

    if strict_dominance:
        return {
            "resolution_status": "DETERMINISTIC_TOP_CANDIDATE",
            "reason_code": "STRICT_GOVERNED_DOMINANCE",
            "candidate_count": len(eligible_candidates),
            "eligible_candidate_ids": eligible_candidate_ids,
            "requested_candidate_id": requested_id,
            "selected_candidate_id": selected_candidate_id,
            "selected_candidate": _candidate_summary(selected_candidate),
            "strict_dominance": True,
        }

    return {
        "resolution_status": "BOUNDED_AMBIGUOUS_SET",
        "reason_code": "AMBIGUOUS_BOUNDED_SET",
        "candidate_count": len(eligible_candidates),
        "eligible_candidate_ids": eligible_candidate_ids,
        "requested_candidate_id": requested_id,
        "selected_candidate_id": "",
        "selected_candidate": None,
        "strict_dominance": False,
    }
