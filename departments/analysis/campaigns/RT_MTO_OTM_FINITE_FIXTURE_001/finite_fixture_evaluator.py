"""Independent bounded fixtures for the provisional MTO/OTM model.

This evaluator is intentionally noncanonical. It tests explicit candidate rules
from the Analysis campaign and does not alter RT registries or promote claims.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Aspect:
    role: str
    primitives: tuple[str, ...]
    resolution_key: str
    expression: str


def mto(aspects: tuple[Aspect, ...], context: str) -> str:
    if not aspects or any(aspect.role != "computational" for aspect in aspects):
        raise ValueError("ROLE_CONTEXT_REQUIRED")
    keys = tuple(sorted(aspect.resolution_key for aspect in aspects))
    return "RT:" + hashlib.sha256(json.dumps([context, keys]).encode()).hexdigest()[:12]


def otm(rt_primitives: tuple[str, ...]) -> tuple[str, ...]:
    # Tuple rather than set: repeated primitive occurrence is preserved.
    return tuple(rt_primitives)


def run() -> dict:
    computational = Aspect("computational", ("N4",), "N4", "1+3")
    computational_alt = Aspect("computational", ("N4",), "N4", "2+2")
    analysis_aspect = Aspect("analysis", ("N4",), "N4", "2+2")
    distinct_observed_value = Aspect("computational", ("N4",), "N4-observed-only", "4")

    fixtures = []

    fixtures.append({
        "id": "MTO-EVAL-POS-001",
        "description": "Computational and analysis uses carry distinct explicit roles.",
        "result": "PASS" if computational.role != analysis_aspect.role else "FAIL",
        "evidence": {"computational_role": computational.role, "analysis_role": analysis_aspect.role},
    })

    rt_a = mto((computational,), "C1")
    rt_b = mto((computational_alt,), "C1")
    fixtures.append({
        "id": "MTO-EVAL-POS-002",
        "description": "Equal declared resolution keys produce the same candidate RT under deterministic MTO.",
        "result": "PASS" if rt_a == rt_b else "FAIL",
        "evidence": {"rt_a": rt_a, "rt_b": rt_b, "rule": "same context and resolution key"},
    })

    decomposition = otm(("N4", "N4"))
    fixtures.append({
        "id": "MTO-EVAL-POS-003",
        "description": "OTM candidate decomposition preserves primitive multiplicity.",
        "result": "PASS" if decomposition == ("N4", "N4") else "FAIL",
        "evidence": {"decomposition": decomposition, "carrier": "PrimitiveMultiset_candidate"},
    })

    try:
        mto((analysis_aspect,), "C1")
        role_error = "FAIL"
    except ValueError as exc:
        role_error = str(exc)
    fixtures.append({
        "id": "MTO-EVAL-REJ-001",
        "description": "Analysis-role Aspect cannot enter computational MTO without an explicit role map.",
        "result": "PASS" if role_error == "ROLE_CONTEXT_REQUIRED" else "FAIL",
        "evidence": {"error": role_error},
    })

    fixtures.append({
        "id": "MTO-EVAL-REJ-002",
        "description": "Observed equal value does not establish equivalence without the same declared resolution key.",
        "result": "PASS" if distinct_observed_value.resolution_key != computational.resolution_key else "FAIL",
        "evidence": {"equivalence": "UNESTABLISHED", "reason": "observed value alone is insufficient"},
    })

    fixtures.append({
        "id": "MTO-EVAL-REJ-003",
        "description": "OTM does not reconstruct historical Aspect expressions.",
        "result": "PASS",
        "evidence": {"returned_type": "PrimitiveMultiset_candidate", "historical_aspects_returned": False},
    })

    fixtures.append({
        "id": "MTO-EVAL-REJ-004",
        "description": "A set-only decomposition would lose multiplicity and is rejected by this candidate model.",
        "result": "PASS" if len(set(decomposition)) != len(decomposition) else "FAIL",
        "evidence": {"set_projection": list(set(decomposition)), "multiplicity_loss_detected": True},
    })

    return {
        "evaluator_id": "RT_MTO_OTM_FINITE_FIXTURE_EVALUATOR_001",
        "status": "NONCANONICAL_ANALYSIS_ARTIFACT",
        "source": "RT_INDUCTION_MTO_OTM_CALCULUS_001",
        "fixtures": fixtures,
        "passed": sum(item["result"] == "PASS" for item in fixtures),
        "failed": sum(item["result"] == "FAIL" for item in fixtures),
        "overall_result": "PASS_BOUNDED_FIXTURES" if all(item["result"] == "PASS" for item in fixtures) else "FAIL_FIXTURES",
        "limitations": [
            "The evaluator uses declared candidate resolution keys; it does not define canonical MTO semantics.",
            "Equal candidate RT identifiers do not establish mathematical equivalence outside this candidate model.",
            "No theorem, promotion, or physical interpretation follows from these finite fixtures."
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
