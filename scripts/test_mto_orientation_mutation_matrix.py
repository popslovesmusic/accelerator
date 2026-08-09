"""Bounded in-memory mutation matrix for provisional orientation fixtures."""
from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "departments/research/reports"
SPEC = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_independent_validation_set.json"
EVIDENCE = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_witness_evidence.json"
OUT = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_mutation_matrix_result.json"


def valid_fixture(fixture: dict, contexts: set[str]) -> bool:
    return (
        fixture.get("context_id") in contexts
        and fixture.get("left") in {"o_a", "o_b"}
        and fixture.get("right") in {"o_a", "o_b"}
        and fixture.get("evidence") in {
            "valid_joint_admissibility_witness",
            "valid_typed_order_witness",
            "valid_exclusive_conflict_witness",
            "conflict_claim_without_witness",
            "ordering_relation_missing",
            "reverse_order_without_rule",
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    contexts = {item["context_id"] for item in spec["contexts"]}
    cases = []
    for fixture in spec["fixtures"]:
        mutations = {
            "context": {**fixture, "context_id": "UNKNOWN_CONTEXT"},
            "left_orientation": {**fixture, "left": "o_x"},
            "right_orientation": {**fixture, "right": "o_x"},
            "evidence": {**fixture, "evidence": "UNREGISTERED_EVIDENCE"},
            "expected_outcome": {**fixture, "expected": "UNAUTHORIZED_RESULT"},
        }
        for mutation, candidate in mutations.items():
            cases.append({
                "fixture_id": fixture["fixture_id"],
                "mutation": mutation,
                "rejected": not valid_fixture(candidate, contexts) if mutation != "expected_outcome" else candidate["expected"] not in {"COMPATIBLE", "ORDERED", "CONFLICT", "INCOMPARABLE_OR_UNRESOLVED", "UNRESOLVED_NOT_CONFLICT", "MALFORMED_OR_UNRESOLVED"},
            })
    control = copy.deepcopy(evidence["disposition"])
    cases.extend([
        {"fixture_id": "CONTROL", "mutation": "active_witnesses", "rejected": control["active_witnesses"] == 0},
        {"fixture_id": "CONTROL", "mutation": "mto_selection", "rejected": control["mto_selection_enabled"] is False},
    ])
    passed = all(case["rejected"] for case in cases)
    payload = {
        "report_id": "RT_INDUCTION_MTO_OTM_CALCULUS_001_MUTATION_MATRIX_RESULT_001",
        "status": "PASS_MUTATION_MATRIX" if passed else "FAIL_MUTATION_MATRIX",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "case_count": len(cases),
        "cases": cases,
        "mutation_scope": "in-memory copies only",
        "witness_activation": "DISABLED",
        "mto_selection": "DISABLED",
        "canonical_math_modified": False,
        "nonclaims": ["This matrix tests bounded rejection behavior only; it does not validate canonical orientation semantics."],
    }
    if args.run:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
