import json
import os
from datetime import datetime

def classify_basins():
    """
    Runner for Recursive Stability Basin Classification.
    Processes campaign logs and assigns basin classes.
    """
    log_dir = "validation/results/campaign_logs"
    registry_path = "registry/math/recursive_stability_basin_classification_registry.json"
    result_path = "validation/results/recursive_stability_basin_classification_summary.json"
    
    if not os.path.exists(log_dir):
        print(f"Log directory {log_dir} missing. Creating dummy result.")
        return {"status": "fail", "reason": "no campaign logs"}

    # Find the latest campaign log
    logs = [f for f in os.listdir(log_dir) if f.startswith("campaign_trace_")]
    if not logs:
         print("No logs found. Creating dummy result.")
         return {"status": "fail", "reason": "no logs found"}
         
    latest_log = sorted(logs)[-1]
    with open(os.path.join(log_dir, latest_log), 'r') as f:
        log_data = json.load(f)

    classification = {
        "summary_id": "RSB-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "basin_assignments": []
    }

    # Classification Logic
    for injection in log_data["injections"]:
        ce_id = injection["counterexample_id"]
        result = injection["result"]
        
        assignment = {
            "counterexample_id": ce_id,
            "basin_class": "RSB-STABLE" # Default
        }
        
        # Map injection results to basin classes
        if "BOUNDARY_HARDENING_TRIGGERED" in result:
             assignment["basin_class"] = "RSB-METASTABLE"
        elif "BLOCKER_PRESERVED" in result:
             # Link to specific classes based on CE type
             if ce_id == "CE-013-002":
                  assignment["basin_class"] = "RSB-SEVERED"
             elif ce_id == "CE-013-003":
                  assignment["basin_class"] = "RSB-OSCILLATORY"
             elif ce_id == "CE-013-004":
                  assignment["basin_class"] = "RSB-AMBIGUOUS"
             else:
                  assignment["basin_class"] = "RSB-METASTABLE"
                  
        classification["basin_assignments"].append(assignment)

    with open(result_path, 'w') as f:
        json.dump(classification, f, indent=2)

    print(f"Classification summary saved to {result_path}")
    return classification

if __name__ == "__main__":
    classify_basins()
