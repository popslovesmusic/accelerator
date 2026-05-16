import json
import os
from datetime import datetime

def validate_orientation_density():
    result_path = "validation/results/orientation_gradient_analysis.json"
    val_out_path = "validation/results/orientation_density_fields_validation_result.json"
    
    report = {
        "validation_id": "VAL-BOFD-ODF-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        if data.get("overcompression_detected"):
             report["status"] = "fail"
             report["governance_violations"].append("orientation overcompression detected in density fields")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_orientation_density()
    print(json.dumps(res, indent=2))
