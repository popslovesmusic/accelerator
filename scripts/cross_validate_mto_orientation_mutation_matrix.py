"""Independent structural cross-check for the mutation matrix report."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "departments/research/reports/RT_INDUCTION_MTO_OTM_CALCULUS_001_mutation_matrix_result.json"
OUT = ROOT / "departments/research/reports/RT_INDUCTION_MTO_OTM_CALCULUS_001_mutation_matrix_cross_validation.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    cases = report.get("cases", [])
    mutation_cases = [case for case in cases if case["fixture_id"] != "CONTROL"]
    controls = [case for case in cases if case["fixture_id"] == "CONTROL"]
    checks = {
        "status_pass": report.get("status") == "PASS_MUTATION_MATRIX",
        "expected_case_count": report.get("case_count") == 42,
        "all_cases_rejected": all(case.get("rejected") is True for case in cases),
        "all_fixture_ids_covered": {case["fixture_id"] for case in mutation_cases} == {f"IND-VAL-{i:03d}" for i in range(1, 9)},
        "five_mutation_dimensions_each": all(sum(case["fixture_id"] == fixture for case in mutation_cases) == 5 for fixture in {case["fixture_id"] for case in mutation_cases}),
        "activation_controls_present": {case["mutation"] for case in controls} == {"active_witnesses", "mto_selection"},
        "activation_disabled": report.get("witness_activation") == "DISABLED" and report.get("mto_selection") == "DISABLED",
        "in_memory_scope": report.get("mutation_scope") == "in-memory copies only",
    }
    passed = all(checks.values())
    payload = {
        "report_id": "RT_INDUCTION_MTO_OTM_CALCULUS_001_MUTATION_MATRIX_CROSS_VALIDATION_001",
        "status": "PASS_MUTATION_MATRIX_CROSS_VALIDATION" if passed else "FAIL_MUTATION_MATRIX_CROSS_VALIDATION",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "witness_activation": "DISABLED",
        "mto_selection": "DISABLED",
        "canonical_math_modified": False,
        "nonclaims": ["This cross-check validates matrix coverage and report integrity only."],
    }
    if args.run:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
