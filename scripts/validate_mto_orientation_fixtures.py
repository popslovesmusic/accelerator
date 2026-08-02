"""Validation-only evaluator for the provisional MTO orientation fixtures."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "departments/research/reports/RT_INDUCTION_MTO_OTM_CALCULUS_001_independent_validation_set.json"
OUT = ROOT / "departments/research/reports/RT_INDUCTION_MTO_OTM_CALCULUS_001_independent_validation_result.json"


def stable_hash(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def evaluate(fixture: dict) -> str:
    evidence = fixture.get("evidence")
    context = fixture.get("context_id")
    if context is None:
        return "INCOMPARABLE_OR_UNRESOLVED"
    if evidence == "valid_joint_admissibility_witness":
        return "COMPATIBLE"
    if evidence == "valid_typed_order_witness":
        return "ORDERED"
    if evidence == "valid_exclusive_conflict_witness":
        return "CONFLICT"
    if evidence == "conflict_claim_without_witness":
        return "UNRESOLVED_NOT_CONFLICT"
    if evidence == "ordering_relation_missing" or evidence == "reverse_order_without_rule":
        return "INCOMPARABLE_OR_UNRESOLVED"
    if evidence == "right_orientation_outside_domain":
        return "MALFORMED_OR_UNRESOLVED"
    return "INCOMPARABLE_OR_UNRESOLVED"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    results = []
    for fixture in spec.get("fixtures", []):
        actual = evaluate(fixture)
        expected = fixture.get("expected")
        results.append({"fixture_id": fixture.get("fixture_id"), "expected": expected, "actual": actual, "match": actual == expected})
    payload = {
        "report_id": "RT_INDUCTION_MTO_OTM_CALCULUS_001_INDEPENDENT_VALIDATION_RESULT_001",
        "specification": str(SPEC.relative_to(ROOT)).replace("\\", "/"),
        "status": "PASS_BOUNDED_FIXTURE_EVALUATION" if all(r["match"] for r in results) else "FAIL_BOUNDED_FIXTURE_EVALUATION",
        "validation_scope": "fixture semantics only; not witness activation",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "input_hash": stable_hash(spec),
        "witness_activation": "DISABLED",
        "mto_selection": "DISABLED",
        "canonical_math_modified": False,
        "nonclaims": ["This run validates the declared bounded fixture evaluator only.", "It does not validate external or canonical orientation semantics."]
    }
    payload["output_hash"] = stable_hash(payload)
    if args.run:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"].startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
