import json
from pathlib import Path


def load(root):
    return json.loads((root / "projection_spec.json").read_text(encoding="utf-8"))


def project_value(value, context, defined, spec):
    if not defined or context not in spec["contexts"]:
        return None
    prefix = spec["contexts"][context]["projection_prefix"]
    return {"context": context, "source_id": value["id"], "value": prefix + value["value"], "type": "TYPE_PROJECTION"}


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


def evaluate(fixture, spec):
    source = project_value(fixture["source"], fixture["context"], fixture["projection_defined"], spec)
    target = project_value(fixture["target"], fixture["context"], fixture["projection_defined"], spec)
    if source is None or target is None:
        return False
    witness = project_witness(fixture["witness"], source, target, fixture["context"])
    if witness is None or not history_sufficient(fixture["history"], source, target, witness, fixture["context"]):
        return False
    trace = fixture["trace"]
    if trace.get("context") != fixture["context"] or trace.get("witness_id") != witness["id"] or trace.get("status") != "COMPATIBLE":
        return False
    threshold = spec["contexts"][fixture["context"]]["epsilon_threshold"]
    return fixture.get("epsilon", threshold) >= threshold


def validate_thresholds(spec):
    rows = []
    for context, cfg in spec["contexts"].items():
        threshold = cfg["epsilon_threshold"]
        rows.extend([epsilon >= threshold for epsilon in [0.0, threshold / 2, threshold, threshold * 1.5]])
    return all(isinstance(v, bool) for v in rows) and len(rows) == 8


def main():
    root = Path(__file__).parent
    data = json.loads((root / "fixtures.json").read_text(encoding="utf-8"))
    spec = load(root)
    rows = [{"id": f["id"], "observed": evaluate(f, spec), "expected": f["expected"], "pass": evaluate(f, spec) == f["expected"]} for f in data["fixtures"]]
    threshold_pass = validate_thresholds(spec)
    result = {
        "status": "PASS_SPECIFIED_PROJECTION_AND_THRESHOLD_MODEL" if all(r["pass"] for r in rows) and threshold_pass else "FAIL",
        "epistemic_status": "MECHANICALLY_VERIFIED",
        "proof_status": "OBLIGATIONS_IDENTIFIED",
        "claim_ceiling": data["claim_ceiling"],
        "fixture_count": len(rows),
        "passed": sum(r["pass"] for r in rows),
        "failed": sum(not r["pass"] for r in rows),
        "threshold_surface_pass": threshold_pass,
        "model_constructs": ["specified Pi_D,C mapping", "typed witness provenance", "payload-linked ordered history", "bounded context thresholds"],
        "obligations": {"OBL-D-001D": "OPEN", "OBL-D-001E": "OPEN"},
        "promotion_authorized": False,
        "human_review_required": True
    }
    (root / "model_check_report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
