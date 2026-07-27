import json
from pathlib import Path


def evaluate(f):
    history_ok = f.get("history") == ["projection_invoked", "witness_bound"]
    e_ok = f.get("epsilon", 1) > 0
    return bool(
        f.get("projection_defined")
        and f.get("witness_provenance")
        and history_ok
        and f.get("payload_aligned")
        and f.get("trace_compatible")
        and e_ok
    )


def main():
    root = Path(__file__).parent
    data = json.loads((root / "fixtures.json").read_text(encoding="utf-8"))
    rows = [{"id": f["id"], "observed": evaluate(f), "expected": f["expected"], "pass": evaluate(f) == f["expected"]} for f in data["fixtures"]]
    result = {
        "status": "PASS_BOUNDED_FORMAL_MODEL" if all(r["pass"] for r in rows) else "FAIL",
        "epistemic_status": "MECHANICALLY_VERIFIED",
        "proof_status": "OBLIGATIONS_IDENTIFIED",
        "claim_ceiling": data["claim_ceiling"],
        "fixture_count": len(rows),
        "passed": sum(r["pass"] for r in rows),
        "failed": sum(not r["pass"] for r in rows),
        "rows": rows,
        "obligations": {"OBL-D-001D": "OPEN", "OBL-D-001E": "OPEN"},
        "promotion_authorized": False,
        "human_review_required": True
    }
    (root / "model_check_report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
