import json
import os
from datetime import datetime

def validate_non_globalization():
    result_path = "validation/results/boundary_symbiosis_analysis.json"
    val_out_path = "validation/results/non_globalization_ecology_validation_result.json"
    
    report = {
        "validation_id": "VAL-RBE-NOGLOB-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        if not data.get("non_globalization_verified"):
             report["status"] = "fail"
             report["governance_violations"].append("non-globalization verification failed in ecology")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_non_globalization()
    print(json.dumps(res, indent=2))
