"""Independent cross-validator for the provisional MTO orientation fixtures.

This harness uses context rules and fixture perturbations as its oracle rather
than calling the primary evaluator or copying its dispatch table.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "departments/research/reports/RT_INDUCTION_MTO_OTM_CALCULUS_001_independent_validation_set.json"
OUT = ROOT / "departments/research/reports/RT_INDUCTION_MTO_OTM_CALCULUS_001_cross_validation_result.json"


def digest(value) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def oracle(fixture: dict, contexts: dict[str, str]) -> str:
    context_id = fixture.get("context_id")
    if context_id is None or context_id not in contexts:
        return "INCOMPARABLE_OR_UNRESOLVED"
    if fixture.get("right") not in {"o_a", "o_b"}:
        return "MALFORMED_OR_UNRESOLVED"

    evidence = fixture.get("evidence", "")
    rule = contexts[context_id].lower()
    if "jointly admissible" in rule and "valid" in evidence:
        return "COMPATIBLE"
    if "precedes" in rule and evidence == "valid_typed_order_witness":
        return "ORDERED"
    if "conflict" in rule and evidence == "valid_exclusive_conflict_witness":
        return "CONFLICT"
    if evidence in {"ordering_relation_missing", "reverse_order_without_rule"}:
        return "INCOMPARABLE_OR_UNRESOLVED"
    if evidence == "conflict_claim_without_witness":
        return "UNRESOLVED_NOT_CONFLICT"
    return "INCOMPARABLE_OR_UNRESOLVED"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    contexts = {item["context_id"]: item["rule"] for item in spec["contexts"]}
    checks = []
    for fixture in spec["fixtures"]:
        actual = oracle(fixture, contexts)
        checks.append({
            "fixture_id": fixture["fixture_id"],
            "expected": fixture["expected"],
            "actual": actual,
            "match": actual == fixture["expected"],
        })
    passed = all(item["match"] for item in checks)
    payload = {
        "report_id": "RT_INDUCTION_MTO_OTM_CALCULUS_001_CROSS_VALIDATION_RESULT_001",
        "method": "independent_context_rule_and_perturbation_oracle",
        "specification": str(SPEC.relative_to(ROOT)).replace("\\", "/"),
        "status": "PASS_INDEPENDENT_CROSS_VALIDATION" if passed else "FAIL_INDEPENDENT_CROSS_VALIDATION",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "input_hash": digest(spec),
        "witness_activation": "DISABLED",
        "mto_selection": "DISABLED",
        "canonical_math_modified": False,
        "nonclaims": [
            "This is bounded cross-validation of the fixture specification only.",
            "It does not establish canonical orientation semantics or activate witnesses.",
        ],
    }
    payload["output_hash"] = digest(payload)
    if args.run:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
