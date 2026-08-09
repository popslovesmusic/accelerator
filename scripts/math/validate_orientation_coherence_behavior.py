import json
import os
from datetime import datetime

def validate_orientation_coherence():
    result_path = "validation/results/orientation_field_coherence_report.json"
    val_out_path = "validation/results/orientation_coherence_behavior_validation_result.json"
    
    report = {
        "validation_id": "VAL-BOFD-COH-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        if not data.get("field_coherence_verified"):
             report["status"] = "fail"
             report["governance_violations"].append("orientation field coherence verification failed")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_orientation_coherence()
    print(json.dumps(res, indent=2))
