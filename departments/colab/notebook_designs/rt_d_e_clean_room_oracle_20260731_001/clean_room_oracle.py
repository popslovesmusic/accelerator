"""Independent D/E oracle derived only from the governed semantic specification.

This module intentionally has no imports from candidate implementations or prior
notebooks. It uses ordinary JSON-compatible records so a clean-room implementer
can reproduce the semantics independently.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def exact_bind(witness: Any, payload: Any) -> bool:
    return isinstance(witness, Mapping) and "token" in witness and witness["token"] == payload


def same_context(context: Any, target_context: Any) -> bool:
    return isinstance(context, str) and isinstance(target_context, str) and context == target_context


def ordered_history(history: Any) -> bool:
    if not isinstance(history, list) or not history:
        return False
    if not all(isinstance(item, Mapping) and "step" in item and "state" in item for item in history):
        return False
    steps = [item["step"] for item in history]
    return all(isinstance(step, int) and not isinstance(step, bool) for step in steps) and all(
        left < right for left, right in zip(steps, steps[1:])
    )


def terminates_at(history: Any, target: Any) -> bool:
    return bool(history) and isinstance(history, list) and isinstance(history[-1], Mapping) and history[-1].get("state") == target


def known_profile(profile: Any, environment: Mapping[str, Any]) -> bool:
    return isinstance(profile, str) and profile in environment and _is_finite_number(environment[profile]) and environment[profile] > 0


def positive_distinction(distinction: Any) -> bool:
    return _is_finite_number(distinction) and distinction > 0


def above_threshold(distinction: Any, profile: Any, environment: Mapping[str, Any]) -> bool:
    return known_profile(profile, environment) and _is_finite_number(distinction) and distinction > environment[profile]


def representable_d(record: Mapping[str, Any], environment: Mapping[str, Any]) -> tuple[bool, str]:
    """Evaluate Representable_D using the declared total precedence."""
    if record.get("relation_type") != "SourceRelation":
        return False, "REJECT_TYPE"
    if not same_context(record.get("context"), record.get("target_context")):
        return False, "REJECT_CONTEXT"
    if not known_profile(record.get("profile"), environment):
        return False, "REJECT_PROFILE"
    witness = record.get("witness")
    if not isinstance(witness, Mapping) or "token" not in witness:
        return False, "REJECT_WITNESS"
    if not exact_bind(witness, record.get("source_payload")):
        return False, "REJECT_WITNESS"
    history = record.get("history")
    if not isinstance(history, list) or not history:
        return False, "REJECT_HISTORY"
    if not ordered_history(history):
        return False, "REJECT_HISTORY"
    if not terminates_at(history, record.get("target")):
        return False, "REJECT_HISTORY"
    return True, "REPRESENTABLE"


def non_collapsed_e(record: Mapping[str, Any], environment: Mapping[str, Any]) -> tuple[bool, str]:
    """Evaluate NonCollapsed_E using strict positive-above-threshold semantics."""
    if not known_profile(record.get("profile"), environment):
        return False, "REJECT_PROFILE"
    distinction = record.get("distinction")
    if not positive_distinction(distinction):
        return False, "REJECT_DISTINCTION"
    if not above_threshold(distinction, record.get("profile"), environment):
        return False, "REJECT_SUBTHRESHOLD"
    return True, "NON_COLLAPSED"


def admissible_de(record: Mapping[str, Any], environment: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    representable, representable_result = representable_d(record, environment)
    non_collapsed, non_collapsed_result = non_collapsed_e(record, environment)
    return representable and non_collapsed, {
        "representable_d": representable_result,
        "non_collapsed_e": non_collapsed_result,
        "admissible_de": representable and non_collapsed,
    }


def evaluate_rows(rows: Sequence[Mapping[str, Any]], environment: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return canonical row-level oracle results without candidate labels."""
    results = []
    for row in rows:
        admitted, detail = admissible_de(row, environment)
        results.append({"row_id": row.get("row_id"), **detail, "admissible_de": admitted})
    return results
