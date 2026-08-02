"""Bounded candidate evaluator for provisional orientation resolution."""
from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    admissible: bool
    score: int
    canonical_key: str


def resolve(candidates: tuple[Candidate, ...]) -> str:
    admissible = [candidate for candidate in candidates if candidate.admissible]
    if not admissible:
        raise ValueError("ORIENTATION_UNRESOLVED_NO_ADMISSIBLE_CANDIDATE")
    # Score is primary; canonical_key is the stable tie-breaker.
    selected = sorted(admissible, key=lambda item: (-item.score, item.canonical_key))[0]
    return selected.candidate_id


def run() -> dict:
    fixtures = []

    fixtures.append({
        "id": "ORI-EVAL-POS-001",
        "description": "Inadmissible candidates are excluded before comparison.",
        "result": "PASS" if resolve((Candidate("blocked", False, 100, "a"), Candidate("valid", True, 1, "b"))) == "valid" else "FAIL",
    })

    fixtures.append({
        "id": "ORI-EVAL-POS-002",
        "description": "Higher admissible comparison score wins.",
        "result": "PASS" if resolve((Candidate("low", True, 2, "a"), Candidate("high", True, 3, "z"))) == "high" else "FAIL",
    })

    tied_forward = resolve((Candidate("orientation-b", True, 5, "b"), Candidate("orientation-a", True, 5, "a")))
    tied_reverse = resolve((Candidate("orientation-a", True, 5, "a"), Candidate("orientation-b", True, 5, "b")))
    fixtures.append({
        "id": "ORI-EVAL-POS-003",
        "description": "Equal-score candidates use canonical-key tie-breaking, independent of discovery order.",
        "result": "PASS" if tied_forward == tied_reverse == "orientation-a" else "FAIL",
        "evidence": {"forward": tied_forward, "reverse": tied_reverse},
    })

    try:
        resolve((Candidate("a", False, 1, "a"), Candidate("b", False, 1, "b")))
        unresolved = "FAIL"
    except ValueError as exc:
        unresolved = str(exc)
    fixtures.append({
        "id": "ORI-EVAL-REJ-001",
        "description": "No admissible orientation produces an explicit unresolved result.",
        "result": "PASS" if unresolved == "ORIENTATION_UNRESOLVED_NO_ADMISSIBLE_CANDIDATE" else "FAIL",
        "evidence": {"error": unresolved},
    })

    fixtures.append({
        "id": "ORI-EVAL-REJ-002",
        "description": "Implementation/discovery order is not a semantic selector.",
        "result": "PASS" if tied_forward == tied_reverse else "FAIL",
    })

    return {
        "evaluator_id": "RT_ORIENTATION_RESOLUTION_FINITE_FIXTURE_EVALUATOR_001",
        "source": "RT_INDUCTION_MTO_OTM_CALCULUS_001",
        "status": "NONCANONICAL_ANALYSIS_ARTIFACT",
        "fixtures": fixtures,
        "passed": sum(item["result"] == "PASS" for item in fixtures),
        "failed": sum(item["result"] == "FAIL" for item in fixtures),
        "overall_result": "PASS_BOUNDED_FIXTURES" if all(item["result"] == "PASS" for item in fixtures) else "FAIL_FIXTURES",
        "limitations": [
            "Score and canonical_key are candidate fixture fields, not canonical orientation semantics.",
            "Tie-breaking determinism does not establish RT identity or MTO equivalence.",
            "No external or physical orientation interpretation is made."
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
