import json
import os
from datetime import datetime

def filter_eligibility():
    """
    Runner for Stable Basin Proof-Eligibility Filtering.
    Evaluates classified basins against proof-eligibility criteria.
    """
    summary_path = "validation/results/recursive_stability_basin_classification_summary.json"
    result_path = "validation/results/stable_basin_proof_eligibility_summary.json"
    
    if not os.path.exists(summary_path):
        return {"status": "fail", "reason": "classification summary missing"}

    with open(summary_path, 'r') as f:
        summary_data = json.load(f)

    eligibility = {
        "filter_id": "PFE-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "eligibility_assignments": []
    }

    # Filtering Logic
    for assignment in summary_data["basin_assignments"]:
        ce_id = assignment["counterexample_id"]
        basin_class = assignment["basin_class"]
        
        pfe_class = "PFE-INELIGIBLE-BLOCKED"
        if basin_class == "RSB-STABLE":
             pfe_class = "PFE-ELIGIBLE-LOCAL"
        elif basin_class == "RSB-METASTABLE":
             pfe_class = "PFE-INELIGIBLE-METASTABLE"
        
        # Special case: review required if status was complex
        if "REVIE" in basin_class:
             pfe_class = "PFE-REVIEW-REQUIRED"
             
        elig_entry = {
            "counterexample_id": ce_id,
            "basin_class": basin_class,
            "eligibility_class": pfe_class,
            "promotion_allowed": False
        }
        eligibility["eligibility_assignments"].append(elig_entry)

    with open(result_path, 'w') as f:
        json.dump(eligibility, f, indent=2)

    print(f"Eligibility summary saved to {result_path}")
    return eligibility

if __name__ == "__main__":
    filter_eligibility()
