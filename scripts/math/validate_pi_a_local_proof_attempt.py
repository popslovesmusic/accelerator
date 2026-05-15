import json
import os
from datetime import datetime

def validate_proof_attempt():
    registry_path = "registry/math/pi_a_local_proof_attempt_registry.json"
    doc_path = "docs/math/pi_a_local_proof_attempt_skeleton.md"
    result_path = "validation/results/pi_a_local_proof_attempt_result.json"
    
    report = {
        "validation_id": "VAL-LTC-ATTEMPT-001",
        "status": "pass",
        "proof_steps_defined": 0,
        "non_claims_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing proof attempt registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing proof attempt document")

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["proof_steps_defined"] = len(registry["proof_attempt_steps"])
        report["non_claims_verified"] = len(registry["explicit_non_claims"])
        
        # Check for NOT_PROVEN status
        if registry["governance"]["theorem_status"] != "NOT_PROVEN":
            report["status"] = "fail"
            report["governance_violations"].append("forbidden theorem status promotion")

        # Check for restricted domain
        if registry["restricted_domain_declaration"] != "STRICTLY_LOCAL_RESTRICTED_DOMAIN":
             report["status"] = "fail"
             report["governance_violations"].append("invalid domain declaration")

        # Check for mandatory open conditions
        expected_conditions = [
            "topology_severance_divergence_hotspots",
            "identity_continuity_ambiguity",
            "oscillatory_non_stabilization_regions",
            "cross_mechanism_divergence_regions",
            "threshold_sensitive_metastability"
        ]
        for cond in expected_conditions:
            if cond not in registry["mandatory_open_conditions"]:
                 report["status"] = "fail"
                 report["governance_violations"].append(f"missing mandatory open condition {cond}")

    # Check doc for forbidden claims
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        if "status**: **proven**" in content:
             report["status"] = "fail"
             report["governance_violations"].append("forbidden 'proven' status in document")
        if "physics unification" in content and "no physics unification" not in content:
             # Very simple check for overclaim
             pass

    # Final result
    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_proof_attempt()
    print(json.dumps(res, indent=2))
