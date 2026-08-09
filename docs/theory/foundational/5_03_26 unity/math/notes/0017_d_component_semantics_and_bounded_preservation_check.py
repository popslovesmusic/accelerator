import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0017_d_component_semantics_and_bounded_preservation_fixtures.json").read_text(encoding="utf-8"))


def preserved(case):
    return (
        case["projection_defined"]
        and case["projected_type_p"] == "TYPE_PROJECTION_C"
        and case["projected_type_q"] == "TYPE_PROJECTION_C"
        and case["projected_witness"]
        and case["trace"] == "COMPATIBLE"
        and case["history"]
    )


results = []
for case in fixtures["cases"]:
    observed = "PRESERVED" if preserved(case) else "NOT_PRESERVED"
    results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})

out = {
    "check_id": "D_COMPONENT_SEMANTICS_PRESERVATION_CHECK_20260726",
    "obligation_id": "OBL-D-001D",
    "status": "PASS_BOUNDED_PRESERVATION_CHECK" if all(x["pass"] for x in results) else "FAIL_BOUNDED_PRESERVATION_CHECK",
    "fixture_count": len(results),
    "passed": sum(x["pass"] for x in results),
    "failed": sum(not x["pass"] for x in results),
    "results": results,
    "limitations": ["finite synthetic fixtures", "candidate projection route", "no universal preservation claim", "OBL-D-001D remains open"]
}
(ROOT / "0017_d_component_semantics_and_bounded_preservation_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
