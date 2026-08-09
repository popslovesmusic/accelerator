import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0021_d_noncollapse_boundary_analysis_fixtures.json").read_text(encoding="utf-8"))


def classify(case):
    if case["left"] == case["right"]:
        return "REJECTED_IDENTITY"
    if case["distinction"] == 0:
        return "REJECTED_ZERO"
    if case["distinction"] <= 0:
        return "REJECTED_NONPOSITIVE"
    if case["distinction"] < fixtures["epsilon_a"]:
        return "REJECTED_SUBTHRESHOLD"
    return "ADMISSIBLE_NONCOLLAPSED"


results = []
for case in fixtures["cases"]:
    observed = classify(case)
    results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})

out = {
    "check_id": "D_NONCOLLAPSE_BOUNDARY_ANALYSIS_CHECK_20260726",
    "obligation_id": "OBL-D-001E",
    "status": "PASS_BOUNDED_NONCOLLAPSE_ANALYSIS" if all(r["pass"] for r in results) else "FAIL_BOUNDED_NONCOLLAPSE_ANALYSIS",
    "epsilon_a": fixtures["epsilon_a"],
    "fixture_count": len(results),
    "passed": sum(r["pass"] for r in results),
    "failed": sum(not r["pass"] for r in results),
    "zero_rejected": any(r["observed"] == "REJECTED_ZERO" and r["expected"] == "REJECTED_ZERO" for r in results),
    "minimum_positive_preserves_distinction": any(r["observed"] == "ADMISSIBLE_NONCOLLAPSED" and r["expected"] == "ADMISSIBLE_NONCOLLAPSED" for r in results),
    "results": results,
    "limitations": ["finite threshold model", "epsilon_a is stipulated not derived", "no physical realization", "full D theorem debt remains open"]
}
(ROOT / "0021_d_noncollapse_boundary_analysis_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
