#!/usr/bin/env python3
"""Validate finite TR-010 density and decoupling fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURES = ROOT / "docs/theory/foundational/5_03_26 unity/math/notes/0035_rt_tr010_density_decoupling_fixtures.json"
DEFAULT_REPORT = ROOT / "docs/theory/foundational/5_03_26 unity/math/notes/0035_rt_tr010_density_decoupling_check_report.json"


def evaluate(case: dict) -> str:
    value = case["input"]
    if any(value.get(key, 0) < 0 for key in ("before", "after", "active_before", "active_after", "released", "reservoir_before", "reservoir_after")):
        return "INVALID_ACCOUNTING"
    operation = value["operation"]
    if operation == "closure":
        return "PASS" if value["before"] == value["after"] else "CLOSURE_NONCONSERVING"
    if operation == "redistribution":
        return "PASS" if value["before"] == value["after"] else "DENSITY_CREATED_OR_LOST"
    if operation == "active":
        return "INERT_STATE_REQUIRED" if value.get("dof") == 0 else "PASS"
    if operation == "decoupling":
        if value.get("dof") != 0:
            return "INVALID_DECOUPLING"
        return "PASS" if value["active_before"] - value["released"] == value["active_after"] and value["reservoir_before"] + value["released"] == value["reservoir_after"] else "INVALID_ACCOUNTING"
    return "INVALID_ACCOUNTING"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    fixtures = json.loads(args.fixtures.read_text(encoding="utf-8"))
    results = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        results.append({"case_id": case["case_id"], "name": case["name"], "status": "PASS" if actual == case["expected"] else "FAIL", "actual": actual, "expected": case["expected"]})
    failed = [item for item in results if item["status"] == "FAIL"]
    report = {"report_id": "0035_rt_tr010_density_decoupling_check_report", "fixture_set_id": fixtures["fixture_set_id"], "status": "PASS" if not failed else "FAIL", "claim_ceiling": fixtures["claim_ceiling"], "case_count": len(results), "passed_count": len(results) - len(failed), "failed_count": len(failed), "results": results, "limitations": ["Finite accounting interface only; density is not treated as a physical quantity.", "No thermodynamic, empirical, or external conservation claim is tested."]}
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
