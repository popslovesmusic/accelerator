import json
import os
from datetime import datetime

def validate_non_closure_stability():
    result_path = "validation/results/adaptive_incompleteness_stabilization_results.json"
    val_out_path = "validation/results/non_closure_stability_validation_result.json"
    
    report = {
        "validation_id": "VAL-AIS-STAB-VALID-001",
        "status": "pass",
        "stabilized_targets": [],
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        for target in data["stabilized_structures"]:
            report["stabilized_targets"].append(target["target_id"])
            if "theorem" in target.get("stabilization_class", ""):
                 report["status"] = "fail"
                 report["governance_violations"].append(f"forbidden theorem-authority in stabilization class for {target['target_id']}")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_non_closure_stability()
    print(json.dumps(res, indent=2))
