import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0018_d_constructed_projection_model_fixtures.json").read_text(encoding="utf-8"))


def evaluate(case):
    source_defined = all(v["type"] == "TYPE_AFFECT_EFFECT" and v["admissible"] for v in (case["x"], case["y"]))
    projection_defined = source_defined and case["projection_route"] == "defined"
    witness_defined = projection_defined and case["witness"] == "bound"
    history_sufficient = set(["projection_invoked", "witness_bound"]).issubset(set(case["history"]))
    return "PRESERVED" if projection_defined and witness_defined and case["trace"] == "compatible" and history_sufficient else "NOT_PRESERVED"


results = []
for case in fixtures["cases"]:
    observed = evaluate(case)
    results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})

out = {
    "check_id": "D_CONSTRUCTED_PROJECTION_MODEL_CHECK_20260726",
    "obligation_id": "OBL-D-001D",
    "status": "PASS_CONSTRUCTED_BOUNDED_MODEL" if all(x["pass"] for x in results) else "FAIL_CONSTRUCTED_BOUNDED_MODEL",
    "fixture_count": len(results),
    "passed": sum(x["pass"] for x in results),
    "failed": sum(not x["pass"] for x in results),
    "results": results,
    "constructed_outputs_used": True,
    "limitations": ["finite synthetic model", "single declared context", "no universal projection semantics", "OBL-D-001D remains open"]
}
(ROOT / "0018_d_constructed_projection_model_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
