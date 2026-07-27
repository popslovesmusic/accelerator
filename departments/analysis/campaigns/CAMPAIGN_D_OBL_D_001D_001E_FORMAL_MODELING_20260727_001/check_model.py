import json
from pathlib import Path


THRESHOLD = 1.0


def project_value(value, context, defined):
    if not defined:
        return None
    return {"context": context, "source_id": value["id"], "value": value["projected"], "type": "TYPE_PROJECTION"}


def project_witness(witness, source, target, context):
    provenance = witness.get("provenance", {})
    if not witness.get("present") or witness.get("context") != context:
        return None
    if provenance.get("context") != context or not provenance.get("relation_id"):
        return None
    if witness.get("source") != source["value"] or witness.get("target") != target["value"]:
        return None
    return {"id": witness["id"], "context": context, "source": source["value"], "target": target["value"], "relation_id": provenance["relation_id"]}


def history_sufficient(history, projected_source, projected_target, witness, context):
    if len(history) != 2 or history[0].get("event") != "projection_invoked" or history[1].get("event") != "witness_bound":
        return False
    invocation, binding = history
    expected = {"context": context, "source": projected_source["value"], "target": projected_target["value"]}
    if any(invocation.get(k) != v for k, v in expected.items()):
        return False
    return all(binding.get(k) == v for k, v in {**expected, "witness_id": witness["id"]}.items())


def evaluate(f):
    source = project_value(f["source"], f["context"], f["projection_defined"])
    target = project_value(f["target"], f["context"], f["projection_defined"])
    if source is None or target is None:
        return False
    witness = project_witness(f["witness"], source, target, f["context"])
    if witness is None or not history_sufficient(f["history"], source, target, witness, f["context"]):
        return False
    trace = f["trace"]
    if trace.get("context") != f["context"] or trace.get("witness_id") != witness["id"] or trace.get("status") != "COMPATIBLE":
        return False
    return f.get("epsilon", THRESHOLD) >= THRESHOLD


def main():
    root = Path(__file__).parent
    data = json.loads((root / "fixtures.json").read_text(encoding="utf-8"))
    rows = []
    for fixture in data["fixtures"]:
        observed = evaluate(fixture)
        rows.append({"id": fixture["id"], "observed": observed, "expected": fixture["expected"], "pass": observed == fixture["expected"]})
    result = {
        "status": "PASS_STRUCTURED_FORMAL_MODEL" if all(r["pass"] for r in rows) else "FAIL",
        "epistemic_status": "MECHANICALLY_VERIFIED",
        "proof_status": "OBLIGATIONS_IDENTIFIED",
        "claim_ceiling": data["claim_ceiling"],
        "fixture_count": len(rows),
        "passed": sum(r["pass"] for r in rows),
        "failed": sum(not r["pass"] for r in rows),
        "rows": rows,
        "model_constructs": ["Pi_D,C projected values", "typed witness provenance", "payload-linked ordered history"],
        "obligations": {"OBL-D-001D": "OPEN", "OBL-D-001E": "OPEN"},
        "promotion_authorized": False,
        "human_review_required": True
    }
    (root / "model_check_report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
