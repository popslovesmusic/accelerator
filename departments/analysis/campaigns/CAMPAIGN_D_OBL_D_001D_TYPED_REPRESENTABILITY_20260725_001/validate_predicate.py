import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
spec = json.loads((ROOT / "representability_predicate_spec.json").read_text(encoding="utf-8"))
fixtures = json.loads((ROOT / "fixtures.json").read_text(encoding="utf-8"))


def evaluate(case):
    return "REPRESENTABLE" if (
        case["p"] == "TYPE_PROJECTION_C"
        and case["q"] == "TYPE_PROJECTION_C"
        and case["witness"] == "typed_relation_witness"
        and case["trace"] == "compatible"
        and case["history"] == "present"
    ) else "NOT_REPRESENTABLE"


results = []
for case in fixtures["cases"]:
    observed = evaluate(case)
    results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})

out = {
    "campaign_id": "CAMPAIGN_D_OBL_D_001D_TYPED_REPRESENTABILITY_20260725_001",
    "obligation_id": "OBL-D-001D",
    "status": "PASS_BOUNDED_CANDIDATE_VALIDATION" if all(item["pass"] for item in results) else "FAIL_CANDIDATE_VALIDATION",
    "predicate_id": spec["predicate_id"],
    "fixture_count": len(results),
    "passed": sum(1 for item in results if item["pass"]),
    "failed": sum(1 for item in results if not item["pass"]),
    "results": results,
    "independence_note": "The validator implements the explicit component conjunction directly and does not use outcome labels to determine representability.",
    "limitations": ["Finite hand-authored fixture set", "Candidate component semantics are not formally mechanized", "Human review remains required", "No obligation discharge claimed"]
}
(ROOT / "validation_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
