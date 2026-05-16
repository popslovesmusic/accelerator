import json
import os
from datetime import datetime

def validate_corridor_density():
    result_path = "validation/results/admissibility_pathway_analysis.json"
    val_out_path = "validation/results/corridor_density_field_validation_result.json"
    
    report = {
        "validation_id": "VAL-FACA-CDF-VALID-001",
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
             report["governance_violations"].append("corridor density overcompression detected in fields")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_corridor_density()
    print(json.dumps(res, indent=2))
