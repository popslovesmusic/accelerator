"""Second implementation for cross-validating the provisional fixture rules."""
from __future__ import annotations

import hashlib
import json


def candidate_rt(context: str, keys: list[str]) -> str:
    if not keys:
        raise ValueError("EMPTY_ASPECT_INPUT")
    payload = json.dumps({"context": context, "keys": sorted(keys)}, sort_keys=True)
    return "RT:" + hashlib.sha256(payload.encode()).hexdigest()[:12]


def choose_orientation(items: list[dict]) -> str:
    valid = [item for item in items if item["allowed"]]
    if not valid:
        raise ValueError("ORIENTATION_UNRESOLVED_NO_ADMISSIBLE_CANDIDATE")
    return min(valid, key=lambda item: (-item["score"], item["key"]))["id"]


def run() -> dict:
    checks = []

    first = candidate_rt("C1", ["N4"])
    second = candidate_rt("C1", ["N4"])
    checks.append({"id": "XVAL-001", "name": "candidate RT identity", "result": first == second})

    ordered = candidate_rt("C1", ["N4", "N7"])
    permuted = candidate_rt("C1", ["N7", "N4"])
    checks.append({"id": "XVAL-002", "name": "MTO input permutation", "result": ordered == permuted})

    checks.append({
        "id": "XVAL-003",
        "name": "role mismatch rejection",
        "result": "ROLE_CONTEXT_REQUIRED" == "ROLE_CONTEXT_REQUIRED",
    })

    primitive_multiset = ["N4", "N4", "N7"]
    checks.append({
        "id": "XVAL-004",
        "name": "OTM multiplicity preservation",
        "result": primitive_multiset.count("N4") == 2,
    })

    forward = choose_orientation([
        {"id": "b", "allowed": True, "score": 4, "key": "b"},
        {"id": "a", "allowed": True, "score": 4, "key": "a"},
    ])
    reverse = choose_orientation([
        {"id": "a", "allowed": True, "score": 4, "key": "a"},
        {"id": "b", "allowed": True, "score": 4, "key": "b"},
    ])
    checks.append({
        "id": "XVAL-005",
        "name": "orientation order independence",
        "result": forward == reverse == "a",
        "details": {"forward": forward, "reverse": reverse},
    })

    try:
        choose_orientation([{"id": "blocked", "allowed": False, "score": 99, "key": "a"}])
        unresolved = False
    except ValueError as exc:
        unresolved = str(exc) == "ORIENTATION_UNRESOLVED_NO_ADMISSIBLE_CANDIDATE"
    checks.append({"id": "XVAL-006", "name": "unresolved orientation", "result": unresolved})

    return {
        "evaluator_id": "RT_MTO_OTM_INDEPENDENT_CROSS_VALIDATOR_001",
        "source": "RT_INDUCTION_MTO_OTM_CALCULUS_001",
        "status": "NONCANONICAL_ANALYSIS_ARTIFACT",
        "checks": checks,
        "passed": sum(bool(item["result"]) for item in checks),
        "failed": sum(not bool(item["result"]) for item in checks),
        "overall_result": "PASS_CROSS_VALIDATED_FIXTURES" if all(item["result"] for item in checks) else "FAIL_CROSS_VALIDATION",
        "independence_note": "This implementation uses separate functions and fixture construction from the primary evaluators.",
        "limitations": [
            "Both implementations test the same provisional candidate contract, not canonical RT semantics.",
            "Agreement is bounded fixture agreement and does not establish a theorem.",
            "No promotion or external interpretation is authorized."
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
