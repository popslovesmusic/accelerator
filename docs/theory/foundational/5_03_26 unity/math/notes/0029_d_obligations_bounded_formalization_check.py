import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0029_d_obligations_bounded_formalization_fixtures.json").read_text(encoding="utf-8"))

def classify(case):
    if case["obligation"] == "OBL-D-001D":
        if not case["same_context"]:
            return "REJECT_CROSS_CONTEXT"
        if not case["witness_bound"]:
            return "REJECT_WITNESS"
        if not case["history_present"]:
            return "REJECT_HISTORY"
        if all(case[k] for k in ("typed", "route_defined", "trace_compatible")):
            return "REPRESENTABLE"
        return "REJECT_TYPED_ROUTE_OR_TRACE"
    if not case["epsilon_positive"] or not case["set_nonempty"]:
        return "REJECT_PROFILE"
    if not case["participants_distinct"] or case["distinction"] == 0:
        return "REJECT_COLLAPSE"
    if case["distinction"] < case["epsilon"]:
        return "REJECT_SUBTHRESHOLD"
    return "NON_COLLAPSED"

results = []
for case in fixtures["cases"]:
    observed = classify(case)
    results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})

out = {
    "check_id": "D_OBLIGATIONS_BOUNDED_FORMALIZATION_CHECK_20260730",
    "obligations": fixtures["obligations"],
    "status": "PASS_BOUNDED_FORMALIZATION_CHECK" if all(r["pass"] for r in results) else "FAIL_BOUNDED_FORMALIZATION_CHECK",
    "fixture_count": len(results),
    "passed": sum(r["pass"] for r in results),
    "failed": sum(not r["pass"] for r in results),
    "claim_ceiling": fixtures["claim_ceiling"],
    "limitations": ["finite declared fixtures", "no universal derivation", "no injectivity or reversibility", "obligations remain open"] ,
    "results": results
}
(ROOT / "0029_d_obligations_bounded_formalization_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
