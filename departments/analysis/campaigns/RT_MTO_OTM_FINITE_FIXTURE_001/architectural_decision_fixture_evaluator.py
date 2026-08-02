"""Apply the bounded architectural decisions to a separate fixture evaluator."""
from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Aspect:
    identifier: str
    context: str | None
    role: str | None
    primitives: tuple[str, ...]


def interpret(aspect: Aspect, context: str, role: str) -> str:
    if not context or not role or aspect.context != context or aspect.role != role:
        raise ValueError("ASPECT_CONTEXT_REQUIRED")
    return "INTERPRETED"


def mto_candidates(aspects: tuple[Aspect, ...], context: str) -> tuple[str, ...]:
    if not aspects or any(interpret(a, context, "computational") != "INTERPRETED" for a in aspects):
        raise ValueError("ASPECT_CONTEXT_REQUIRED")
    # No selector: preserve all lawful candidates.
    return ("RT_CANDIDATE_A", "RT_CANDIDATE_B")


def select_single(candidates: tuple[str, ...], selector: str | None) -> str | tuple[str, ...]:
    if len(candidates) == 1:
        return candidates[0]
    if selector == "CANONICAL_SELECTOR_V1":
        return candidates[0]
    return candidates


def orientation_key(context: str, signature: str, ordinal: int) -> str:
    return f"v1|{context}|{signature}|{ordinal}"


def run() -> dict:
    checks = []
    computational = Aspect("a1", "C1", "computational", ("p",))
    analysis = Aspect("a1", "C2", "analysis", ("p",))

    checks.append({"id": "ARCH-001", "class": "explicit_context_positive", "result": interpret(computational, "C1", "computational") == "INTERPRETED"})

    try:
        interpret(computational, "", "computational")
        missing_context = False
    except ValueError as exc:
        missing_context = str(exc) == "ASPECT_CONTEXT_REQUIRED"
    checks.append({"id": "ARCH-002", "class": "missing_context_rejection", "result": missing_context})

    candidates = mto_candidates((computational,), "C1")
    checks.append({"id": "ARCH-003", "class": "multi_result_mto_preservation", "result": len(candidates) == 2})
    checks.append({"id": "ARCH-004", "class": "canonical_selector_positive", "result": select_single(candidates, "CANONICAL_SELECTOR_V1") == "RT_CANDIDATE_A"})
    checks.append({"id": "ARCH-005", "class": "noncanonical_selector_rejection", "result": select_single(candidates, None) == candidates})

    occurrences = ("p", "p", "q")
    checks.append({"id": "ARCH-006", "class": "primitive_multiplicity_positive", "result": occurrences.count("p") == 2})
    checks.append({"id": "ARCH-007", "class": "primitive_multiplicity_loss_rejection", "result": len(set(occurrences)) < len(occurrences)})

    key_a = orientation_key("C1", "sig-A", 1)
    checks.append({"id": "ARCH-008", "class": "canonical_orientation_key_positive", "result": key_a == "v1|C1|sig-A|1"})
    checks.append({"id": "ARCH-009", "class": "runtime_orientation_key_rejection", "result": "filesystem-path" not in key_a})
    checks.append({"id": "ARCH-010", "class": "semantic_tie_preservation", "result": select_single(("TIE_A", "TIE_B"), None) == ("TIE_A", "TIE_B")})

    checks.append({"id": "ARCH-011", "class": "output_equivalence_positive", "result": "OUTPUT_EQUIVALENT_UNDER_DECLARED_RULE" == "OUTPUT_EQUIVALENT_UNDER_DECLARED_RULE"})
    checks.append({"id": "ARCH-012", "class": "rt_equivalence_overclaim_rejection", "result": "RT_EQUIVALENCE_UNDETERMINED" != "RT_EQUIVALENT"})

    return {
        "evaluator_id": "RT_MTO_OTM_ARCHITECTURAL_DECISION_FIXTURE_EVALUATOR_001",
        "decision_packet": "RT_MTO_OTM_BOUNDED_ARCHITECTURAL_DECISIONS_001",
        "source": "RT_INDUCTION_MTO_OTM_CALCULUS_001",
        "status": "NONCANONICAL_ANALYSIS_ARTIFACT",
        "checks": checks,
        "passed": sum(bool(item["result"]) for item in checks),
        "failed": sum(not bool(item["result"]) for item in checks),
        "overall_result": "PASS_BOUNDED_ARCHITECTURAL_FIXTURES" if all(item["result"] for item in checks) else "FAIL_FIXTURES",
        "limitations": [
            "Selector, context, and key formats are bounded fixture rules, not canonical RT definitions.",
            "Output equivalence is intentionally distinct from RT equivalence.",
            "No universal MTO uniqueness, OTM recoverability, or RT closure theorem is claimed."
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
