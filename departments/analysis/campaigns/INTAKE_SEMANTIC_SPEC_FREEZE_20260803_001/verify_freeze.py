import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    spec_path = ROOT / "departments/analysis/campaigns/INTAKE_SEMANTIC_SPEC_FREEZE_20260803_001/frozen_semantics.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    prior = json.loads((ROOT / "departments/analysis/campaigns/INTAKE_BROADER_MODEL_CLASS_20260803_001/results.json").read_text(encoding="utf-8"))
    repaired = json.loads((ROOT / "departments/analysis/campaigns/INTAKE_REPAIRED_SEMANTICS_20260803_001/results.json").read_text(encoding="utf-8"))
    checks = [
        spec.get("status") == "FROZEN_NONCANONICAL_C1",
        spec.get("promotion_status") == "HOLD_C1",
        spec.get("canonicality") == "NON_CANONICAL",
        prior.get("status") == "PASS_BOUNDED_MODEL_CLASS" and prior.get("failure_count") == 0,
        repaired.get("status") == "PASS_REPAIRED_FINITE_SEMANTICS" and repaired.get("failed") == 0,
        "falsification_policy" in spec,
    ]
    digest = hashlib.sha256(spec_path.read_bytes()).hexdigest().upper()
    payload = {
        "verification_id": "INTAKE_SEMANTIC_SPEC_FREEZE_20260803_001",
        "status": "PASS_FROZEN_SPEC_VERIFICATION" if all(checks) else "FAIL_FROZEN_SPEC_VERIFICATION",
        "checks_run": len(checks),
        "checks_passed": sum(checks),
        "checks_failed": len(checks) - sum(checks),
        "spec_sha256": digest,
        "frozen_spec_path": str(spec_path.relative_to(ROOT)),
        "claim_ceiling": "C1",
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
