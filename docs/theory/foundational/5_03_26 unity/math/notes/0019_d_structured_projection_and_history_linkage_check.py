import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0019_d_structured_projection_and_history_linkage_fixtures.json").read_text(encoding="utf-8"))


def project_value(node, context, route):
    if node["type"] != "TYPE_AFFECT_EFFECT" or not node["admissible"] or route != "defined":
        return None
    return {"context": context, "source_id": node["id"], "value": f"p_{node['id']}", "type": "TYPE_PROJECTION"}


def project_witness(witness, source, target, context):
    if not witness["bound"] or source is None or target is None or source["context"] != context or target["context"] != context:
        return None
    return {"witness_id": witness["id"], "context": context, "source": source["value"], "target": target["value"], "relation": "RELATION_C", "type": "TYPE_RELATION_WITNESS_C"}


def history_sufficient(history, witness, source, target, context):
    if len(history) < 2 or history[0].get("event") != "projection_invoked" or history[1].get("event") != "witness_bound":
        return False
    projection_event, witness_event = history[0], history[1]
    return (
        projection_event.get("context") == context
        and projection_event.get("source") == source["value"]
        and projection_event.get("target") == target["value"]
        and witness_event.get("context") == context
        and witness_event.get("witness_id") == witness["witness_id"]
    )


results = []
for case in fixtures["cases"]:
    context = fixtures["context"]
    source = project_value(case["x"], context, case["projection_route"])
    target = project_value(case["y"], context, case["projection_route"])
    witness = project_witness(case["witness"], source, target, context)
    preserved = all((source, target, witness)) and case["trace"] == "compatible" and history_sufficient(case["history"], witness, source, target, context)
    observed = "PRESERVED" if preserved else "NOT_PRESERVED"
    results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})

out = {
    "check_id": "D_STRUCTURED_PROJECTION_HISTORY_LINKAGE_CHECK_20260726",
    "obligation_id": "OBL-D-001D",
    "status": "PASS_STRUCTURED_BOUNDED_MODEL" if all(r["pass"] for r in results) else "FAIL_STRUCTURED_BOUNDED_MODEL",
    "fixture_count": len(results),
    "passed": sum(r["pass"] for r in results),
    "failed": sum(not r["pass"] for r in results),
    "structured_outputs_constructed": True,
    "history_order_payload_identity_checked": True,
    "results": results,
    "limitations": ["finite synthetic model", "single declared context", "no universal projection semantics", "OBL-D-001D remains open"]
}
(ROOT / "0019_d_structured_projection_and_history_linkage_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
