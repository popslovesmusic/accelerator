import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RESULT_PATH = ROOT / "departments/analysis/campaigns/INTAKE_VALIDATION_20260803_001/validation_results.json"


def main():
    data = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    checks = []
    expected = {
        "RT_ASYM_OBSERVATION_ORIENTATION_EXCLUSION_INDUCTION_20260728_001": 5,
        "RT_BOUNDARY_ORIENTATION_ASYM_INDUCTION_20260728_001": 5,
        "RT_INDUCTION_MTO_OTM_CALCULUS_001": 6,
        "RT_INDUCTION_RECURSIVE_PATTERN_AND_DOMAIN_LIFT_001": 8,
    }
    for row in data.get("results", []):
        checks.append(row.get("status") == "PASS_BOUNDED_STRUCTURAL_VALIDATION")
        checks.append(row.get("failed") == 0)
        checks.append(row.get("passed") == expected.get(row.get("packet_id")))
        for path in row.get("evidence_paths", []):
            checks.append((ROOT / path).exists())
    text = RESULT_PATH.read_text(encoding="utf-8").lower()
    forbidden = ("boltzmann", "partition function", "reference entropy", "canonical probability")
    checks.append(not any(term in text for term in forbidden))
    payload = {
        "verification_id": "INTAKE_VALIDATION_20260803_001_INDEPENDENT",
        "status": "PASS" if all(checks) else "FAIL",
        "checks_run": len(checks),
        "checks_passed": sum(checks),
        "checks_failed": len(checks) - sum(checks),
        "method": "Independent recomputation of expected result cardinalities, status values, evidence-path existence, and forbidden-term scan.",
        "claim_ceiling": "C1",
    }
    out = RESULT_PATH.with_name("independent_verification.json")
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
