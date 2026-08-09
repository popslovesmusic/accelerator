"""Adversarial finite cases for the provisional MTO/OTM candidate contract."""
from __future__ import annotations

import json


def set_projection(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def resolve_ties(candidates: list[dict]) -> str:
    keys = [item["key"] for item in candidates if item["allowed"]]
    if not keys:
        raise ValueError("NO_ADMISSIBLE_ORIENTATION")
    if len(keys) != len(set(keys)):
        raise ValueError("DUPLICATE_CANONICAL_TIE_KEY")
    return min(keys)


def detect_nondeterminism(outputs: list[str]) -> str:
    return "NONDETERMINISTIC_OUTPUT" if len(set(outputs)) > 1 else "SINGLE_OUTPUT"


def run() -> dict:
    cases = [
        {
            "id": "ADV-001",
            "name": "context collision",
            "observation": "same primitives under distinct contexts",
            "result": "CONTEXT_MUST_BE_INPUT",
            "counterexample": True,
        },
        {
            "id": "ADV-002",
            "name": "multiplicity collapse",
            "observation": set_projection(("N4", "N4", "N7")) == set_projection(("N4", "N7")),
            "result": "SET_PROJECTION_COLLIDES_DISTINCT_MULTISETS",
            "counterexample": True,
        },
        {
            "id": "ADV-003",
            "name": "duplicate tie key",
            "observation": None,
            "result": None,
            "counterexample": True,
        },
        {
            "id": "ADV-004",
            "name": "nondeterministic MTO candidate",
            "observation": detect_nondeterminism(["RT:a", "RT:b"]),
            "result": "MTO_SINGLE_VALUEDNESS_REQUIRED",
            "counterexample": True,
        },
        {
            "id": "ADV-005",
            "name": "equal output overreach",
            "observation": "two organizations share one observed output",
            "result": "OPERAND_EQUIVALENCE_UNESTABLISHED",
            "counterexample": True,
        },
    ]

    try:
        resolve_ties([{"allowed": True, "key": "same"}, {"allowed": True, "key": "same"}])
        cases[2]["result"] = "FAIL_TO_REJECT_DUPLICATE_KEY"
    except ValueError as exc:
        cases[2]["observation"] = str(exc)
        cases[2]["result"] = "DUPLICATE_CANONICAL_TIE_KEY_REJECTED"

    return {
        "suite_id": "RT_MTO_OTM_ADVERSARIAL_COUNTEREXAMPLE_SUITE_001",
        "source": "RT_INDUCTION_MTO_OTM_CALCULUS_001",
        "status": "NONCANONICAL_ANALYSIS_ARTIFACT",
        "cases": cases,
        "counterexamples_found": sum(case["counterexample"] for case in cases),
        "overall_result": "COUNTEREXAMPLES_FOUND_BOUNDARY_REOPENED",
        "interpretation": "The provisional model must retain explicit context, multiplicity, unique tie keys, and single-valued MTO selection. Equal observed outputs do not establish operand equivalence.",
        "limitations": [
            "These are finite candidate counterexamples, not counterexamples to canonical RT mathematics.",
            "No canonical relation, theorem, or external interpretation is inferred."
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
