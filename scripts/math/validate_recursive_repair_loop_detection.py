import json
import os
from datetime import datetime

def validate_repair_loops():
    result_path = "validation/results/adaptive_incompleteness_stabilization_results.json"
    val_out_path = "validation/results/recursive_repair_loop_validation_result.json"
    
    report = {
        "validation_id": "VAL-AIS-LOOP-VALID-001",
        "status": "pass",
        "loops_detected": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        report["loops_detected"] = data.get("recursive_repair_loops_detected", 0)
        
        if report["loops_detected"] > 10: # Arbitrary threshold for systemic loop risk
             report["status"] = "fail"
             report["governance_violations"].append("systemic recursive repair loops detected")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_repair_loops()
    print(json.dumps(res, indent=2))
