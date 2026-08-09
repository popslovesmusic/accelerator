import json
import os
from datetime import datetime

def run_consolidation():
    """
    Runner for Restricted Local Stability Consolidation.
    Consolidates audited proof segment behavior.
    """
    audit_path = "validation/results/restricted_local_proof_consistency_audit_summary.json"
    eligibility_path = "validation/results/stable_basin_proof_eligibility_summary.json"
    result_path = "validation/results/restricted_local_stability_consolidation_summary.json"
    
    if not os.path.exists(audit_path):
        return {"status": "fail", "reason": "consistency audit summary missing"}

    with open(audit_path, 'r') as f:
        audit_data = json.load(f)
        
    with open(eligibility_path, 'r') as f:
        elig_data = json.load(f)

    consolidation = {
        "consolidation_id": "RLSC-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "stable_basins_consolidated": [],
        "mandatory_blockers_maintained": True
    }

    # Consolidation Logic
    for assignment in elig_data["eligibility_assignments"]:
        ce_id = assignment["counterexample_id"]
        pfe_class = assignment["eligibility_class"]
        
        if pfe_class == "PFE-ELIGIBLE-LOCAL":
             # Check if audit was consistent
             consistent = all(v["status"] == "CONSISTENT" for v in audit_data["verifications"])
             
             assignment_entry = {
                 "counterexample_id": ce_id,
                 "consolidation_class": "RLSC-STABLE-LOCAL" if consistent else "RLSC-UNRESOLVED",
                 "promotion_allowed": False
             }
             consolidation["stable_basins_consolidated"].append(assignment_entry)

    with open(result_path, 'w') as f:
        json.dump(consolidation, f, indent=2)

    print(f"Stability consolidation summary saved to {result_path}")
    return consolidation

if __name__ == "__main__":
    run_consolidation()
