import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0028_preservation_claim_boundary_fixtures.json").read_text(encoding="utf-8"))


def classify(case):
    if not case["typed"]:
        return "BLOCKED_UNTYPED"
    claim = case["claim"]
    if "all domains" in claim:
        return "BLOCKED_UNIVERSAL"
    if "injective" in claim:
        return "BLOCKED_INJECTIVITY"
    if "reversible" in claim:
        return "BLOCKED_REVERSIBILITY"
    if "complete information" in claim:
        return "BLOCKED_COMPLETE_INFORMATION"
    if "physically valid" in claim:
        return "BLOCKED_EXTERNAL_PHYSICS"
    if case["scope"] == "finite" and case["history"] and case["fixtures"] and case["limitations"]:
        return "C1_ALLOWED"
    return "BLOCKED_INSUFFICIENT_SCOPE"


results = []
for case in fixtures["claims"]:
    observed = classify(case)
    results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})

out = {
    "check_id": "PRESERVATION_CLAIM_BOUNDARY_CHECK_20260726",
    "related_obligation": "OBL-D-001D",
    "status": "PASS_CLAIM_BOUNDARY_CHECK" if all(r["pass"] for r in results) else "FAIL_CLAIM_BOUNDARY_CHECK",
    "fixture_count": len(results),
    "passed": sum(r["pass"] for r in results),
    "failed": sum(not r["pass"] for r in results),
    "bounded_c1_allowed": True,
    "stronger_claims_blocked": True,
    "results": results,
    "limitations": ["classification boundary only", "no obligation discharge", "no theorem or physical promotion"]
}
(ROOT / "0028_preservation_claim_boundary_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
