import json
import os
import argparse

def validate_rc001_gap_audit():
    results = {
        "rc001_proof_candidate_gap_audit_validation": {
            "status": "pass",
            "gaps_found": [],
            "warnings": [],
            "errors": []
        }
    }

    gap_reg = "registry/math/rc001_proof_candidate_gap_registry.json"
    blocker_reg = "registry/math/rc001_remaining_blocker_registry.json"

    try:
        with open(gap_reg, 'r') as f: g_data = json.load(f).get("rc001_proof_candidate_gap", {})
        with open(blocker_reg, 'r') as f: b_data = json.load(f).get("rc001_remaining_blocker_set", {})
    except Exception as e:
        results["rc001_proof_candidate_gap_audit_validation"]["status"] = "fail"
        results["rc001_proof_candidate_gap_audit_validation"]["errors"].append(f"Load error: {e}")
        return results

    # Identify domains that failed in the gap registry
    for domain, info in g_data.get("domains", {}).items():
        if info.get("status") == "fail":
            results["rc001_proof_candidate_gap_audit_validation"]["gaps_found"].append(f"Domain {domain}: {info.get('basis')}")

    # Verify blockers are recorded
    if len(b_data.get("blockers", [])) == 0:
         results["rc001_proof_candidate_gap_audit_validation"]["status"] = "fail"
         results["rc001_proof_candidate_gap_audit_validation"]["errors"].append("Remaining blocker set is empty but gaps exist.")

    # Explicit check for RC-001 vs RC-002 differences
    if g_data.get("comparison_benchmark") != "RC-002":
         results["rc001_proof_candidate_gap_audit_validation"]["status"] = "fail"
         results["rc001_proof_candidate_gap_audit_validation"]["errors"].append("Benchmarking target mismatch.")

    return results

if __name__ == "__main__":
    res = validate_rc001_gap_audit()
    print(json.dumps(res, indent=2))
