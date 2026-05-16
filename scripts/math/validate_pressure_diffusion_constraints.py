import json
import os
from datetime import datetime

def validate_pressure_diffusion():
    result_path = "validation/results/epistemic_pressure_field_map.json"
    val_out_path = "validation/results/pressure_diffusion_validation_result.json"
    
    report = {
        "validation_id": "VAL-RBE-DIFF-VALID-001",
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
             report["governance_violations"].append("epistemic overcompression detected in pressure fields")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_pressure_diffusion()
    print(json.dumps(res, indent=2))
