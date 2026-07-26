import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0020_d_multicontext_preservation_analysis_fixtures.json").read_text(encoding="utf-8"))


def projected(node, context):
    if node["type"] != "TYPE_AFFECT_EFFECT" or not node["admissible"] or fixtures["contexts"][context]["route"] != "defined":
        return None
    return {"context": context, "value": f"p_{node['id']}"}


def preserved(case):
    context = case["context"]
    source, target = projected(case["x"], context), projected(case["y"], context)
    if source is None or target is None or case["witness_context"] != context or case["trace"] != "compatible":
        return False
    history = case["history"]
    if len(history) < 2 or history[0].get("event") != "projection_invoked" or history[1].get("event") != "witness_bound":
        return False
    return (
        history[0].get("context") == context
        and history[0].get("source") == source["value"]
        and history[0].get("target") == target["value"]
        and history[1].get("context") == context
        and history[1].get("witness_id") == case["witness_id"]
    )


results = []
for case in fixtures["cases"]:
    observed = "PRESERVED" if preserved(case) else "NOT_PRESERVED"
    results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})

out = {
    "check_id": "D_MULTICONTEXT_PRESERVATION_ANALYSIS_CHECK_20260726",
    "obligation_id": "OBL-D-001D",
    "status": "PASS_MULTICONTEXT_BOUNDED_ANALYSIS" if all(r["pass"] for r in results) else "FAIL_MULTICONTEXT_BOUNDED_ANALYSIS",
    "context_count": len(fixtures["contexts"]),
    "fixture_count": len(results),
    "passed": sum(r["pass"] for r in results),
    "failed": sum(not r["pass"] for r in results),
    "context_isolation_checked": True,
    "results": results,
    "limitations": ["finite synthetic contexts", "three declared contexts", "no universal projection semantics", "OBL-D-001E remains open"]
}
(ROOT / "0020_d_multicontext_preservation_analysis_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
