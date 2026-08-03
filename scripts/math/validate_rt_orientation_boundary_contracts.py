#!/usr/bin/env python3
"""Fail-closed validator for the bounded RT orientation/coupling fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURES = ROOT / "docs/theory/foundational/5_03_26 unity/math/notes/0032_rt_orientation_boundary_coupling_contracts_fixtures.json"
DEFAULT_REPORT = ROOT / "docs/theory/foundational/5_03_26 unity/math/notes/0032_rt_orientation_boundary_coupling_contracts_check_report.json"


def check(case: dict) -> tuple[bool, str]:
    case_id = case["case_id"]
    actual = case["input"]
    expected = case["expected"]
    if case_id == "ROLE-001":
        ok = actual["rt_id"] == "RT-1" and actual["roles"][0] != actual["roles"][1]
    elif case_id == "SUFF-001":
        ok = actual["closed"] and actual["sufficient"] and actual["child_status"] == "not_needed"
    elif case_id == "SUFF-002":
        ok = not actual["closed"] and not actual["sufficient"] and actual["child_status"] == "unresolved"
    elif case_id == "ORDER-001":
        ok = actual["permutation"] != list(range(len(actual["bytes"])))
    elif case_id == "COUPLE-001":
        ok = actual["coupling_site"] == "boundary" and actual["interior_transfer"] is False and actual["boundary_update"] is True
    elif case_id == "PROP-001":
        ok = actual["carrier"] == actual["target_carrier"] and actual["cross_boundary_transfer"] is False
    elif case_id == "CLOSE-001":
        ok = actual["children"] == actual["output_order"] and actual["closed_children"] is True and actual["scalar_estimate_at_evaluation"] is False
    elif case_id == "EVAL-001":
        ok = actual["evaluation_output_type"] == "orientation_field" and actual["scalar_magnitude"] is None and actual["downstream_estimate"] == "angle"
    else:
        return False, f"unknown fixture case: {case_id}"
    return ok, "PASS" if ok else f"input does not satisfy declared fixture: {expected}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    fixtures = json.loads(args.fixtures.read_text(encoding="utf-8"))
    results = []
    for case in fixtures["cases"]:
        passed, detail = check(case)
        results.append({"case_id": case["case_id"], "name": case["name"], "status": "PASS" if passed else "FAIL", "detail": detail})
    failed = [result for result in results if result["status"] != "PASS"]
    report = {
        "report_id": "0032_rt_orientation_boundary_coupling_contracts_check_report",
        "fixture_set_id": fixtures["fixture_set_id"],
        "status": "PASS" if not failed else "FAIL",
        "claim_ceiling": fixtures["claim_ceiling"],
        "case_count": len(results),
        "passed_count": len(results) - len(failed),
        "failed_count": len(failed),
        "results": results,
        "limitations": [
            "These are finite contract fixtures, not proof of the RT framework.",
            "No physical geometry, transport, thermodynamic, or external interpretation is tested.",
            "The validator checks declared fixture invariants only."
        ]
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
