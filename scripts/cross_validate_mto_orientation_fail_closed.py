"""Independent report-level cross-check for fail-closed adversarial tests."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "departments/research/reports/RT_INDUCTION_MTO_OTM_CALCULUS_001_fail_closed_result.json"
OUT = ROOT / "departments/research/reports/RT_INDUCTION_MTO_OTM_CALCULUS_001_fail_closed_cross_validation.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    expected = {
        "ADV-HASH-001": "source hash mismatch",
        "ADV-CONTEXT-001": "unknown context binding",
        "ADV-OUTCOME-001": "conflicting expected outcome",
        "ADV-ACTIVATE-001": "attempted witness activation",
        "ADV-MTO-001": "attempted MTO selection enablement",
        "ADV-IMMUTABILITY-001": "canonical inputs unchanged",
    }
    observed = {item["test_id"]: item for item in report.get("tests", [])}
    checks = []
    for test_id, condition in expected.items():
        item = observed.get(test_id, {})
        checks.append({
            "test_id": test_id,
            "condition_matches": item.get("condition") == condition,
            "passed": item.get("rejected") is True,
        })
    passed = (
        report.get("status") == "PASS_FAIL_CLOSED_ADVERSARIAL_TESTS"
        and report.get("mutation_scope") == "in-memory copies only"
        and report.get("witness_activation") == "DISABLED"
        and report.get("mto_selection") == "DISABLED"
        and all(item["condition_matches"] and item["passed"] for item in checks)
    )
    payload = {
        "report_id": "RT_INDUCTION_MTO_OTM_CALCULUS_001_FAIL_CLOSED_CROSS_VALIDATION_001",
        "status": "PASS_FAIL_CLOSED_CROSS_VALIDATION" if passed else "FAIL_FAIL_CLOSED_CROSS_VALIDATION",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "witness_activation": "DISABLED",
        "mto_selection": "DISABLED",
        "canonical_math_modified": False,
        "nonclaims": ["This cross-check validates the adversarial report structure and outcomes only."],
    }
    if args.run:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
