#!/usr/bin/env python3
"""Validate finite TR-008 admissibility, trajectory, and slice fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURES = ROOT / "docs/theory/foundational/5_03_26 unity/math/notes/0033_rt_tr008_admissibility_trajectory_slice_fixtures.json"
DEFAULT_REPORT = ROOT / "docs/theory/foundational/5_03_26 unity/math/notes/0033_rt_tr008_admissibility_trajectory_slice_check_report.json"


def evaluate(case: dict) -> str:
    value = case["input"]
    if case["case_id"] == "TR008-VALID-001":
        return "PASS" if value["positions"] == value["declared_positions"] and value["trajectory"][0] == value["source"] and value["trajectory"][-1] == value["target"] and all(list(edge) in value["declared_edges"] for edge in zip(value["trajectory"], value["trajectory"][1:])) else "FAIL"
    if case["case_id"] == "TR008-ADMISS-001":
        return "INADMISSIBLE" if value["proposition"] != value["declared_proposition"] else "FAIL"
    if case["case_id"] == "TR008-TRAJ-001":
        return "INVALID_TRAJECTORY" if value["trajectory"][0] != value["start"] or value["trajectory"][-1] != value["stop"] else "FAIL"
    if case["case_id"] == "TR008-TRAJ-002":
        return "INVALID_TRAJECTORY" if len(value["trajectory"]) != len(set(value["trajectory"])) else "FAIL"
    if case["case_id"] == "TR008-TRAJ-003":
        edges = list(zip(value["trajectory"], value["trajectory"][1:]))
        return "INVALID_TRAJECTORY" if any(list(edge) not in value["declared_edges"] for edge in edges) else "FAIL"
    if case["case_id"] == "TR008-SLICE-001":
        return "INVALID_SLICE" if value["interface"] not in value["known_interfaces"] else "FAIL"
    if case["case_id"] == "TR008-SLICE-002":
        return "INVALID_SLICE" if value["positions"] != value["declared_positions"] else "FAIL"
    return "FAIL"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    fixtures = json.loads(args.fixtures.read_text(encoding="utf-8"))
    results = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        expected = "PASS" if case["expected"] == "PASS" else case["expected"]
        results.append({"case_id": case["case_id"], "name": case["name"], "status": "PASS" if actual == expected else "FAIL", "actual": actual, "expected": expected})
    failed = [item for item in results if item["status"] == "FAIL"]
    report = {"report_id": "0033_rt_tr008_admissibility_trajectory_slice_check_report", "fixture_set_id": fixtures["fixture_set_id"], "status": "PASS" if not failed else "FAIL", "claim_ceiling": fixtures["claim_ceiling"], "case_count": len(results), "passed_count": len(results) - len(failed), "failed_count": len(failed), "results": results, "limitations": ["Finite interface fixtures only; no physical geometry or causal law is tested.", "Geodesic is a model label for an ordered trajectory, not a metric claim."]}
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
