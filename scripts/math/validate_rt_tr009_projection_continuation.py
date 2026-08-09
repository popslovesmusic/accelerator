#!/usr/bin/env python3
"""Validate finite TR-009 projection-to-RT pipeline fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURES = ROOT / "docs/theory/foundational/5_03_26 unity/math/notes/0034_rt_tr009_projection_continuation_fixtures.json"
DEFAULT_REPORT = ROOT / "docs/theory/foundational/5_03_26 unity/math/notes/0034_rt_tr009_projection_continuation_check_report.json"


def evaluate(case: dict, required: list[str]) -> str:
    value = case["input"]
    stages = value.get("stages", [])
    if stages != required or not value.get("organization_nonempty", False) or not value.get("continuation_finite", False):
        return "INVALID_PIPELINE"
    if value.get("condition_id") == value.get("rt_id"):
        return "ONTOLOGY_COLLAPSE"
    if len(set(value.get("stage_propositions", [value.get("proposition")])) ) != 1 or len(set(value.get("stage_provenance", [value.get("provenance")])) ) != 1:
        return "CONTEXT_DRIFT"
    return "PASS"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    fixtures = json.loads(args.fixtures.read_text(encoding="utf-8"))
    results = []
    for case in fixtures["cases"]:
        actual = evaluate(case, fixtures["required_stages"])
        results.append({"case_id": case["case_id"], "name": case["name"], "status": "PASS" if actual == case["expected"] else "FAIL", "actual": actual, "expected": case["expected"]})
    failed = [item for item in results if item["status"] == "FAIL"]
    report = {"report_id": "0034_rt_tr009_projection_continuation_check_report", "fixture_set_id": fixtures["fixture_set_id"], "status": "PASS" if not failed else "FAIL", "claim_ceiling": fixtures["claim_ceiling"], "case_count": len(results), "passed_count": len(results) - len(failed), "failed_count": len(failed), "results": results, "limitations": ["Finite pipeline interface only; no external ontology or physical projection is tested.", "The validator does not define the internal mathematics of projection or continuation."]}
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
