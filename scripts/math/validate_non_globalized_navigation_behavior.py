import json
import os
from datetime import datetime

def validate_non_globalized_navigation():
    result_path = "validation/results/corridor_coherence_report.json"
    val_out_path = "validation/results/non_globalized_navigation_validation_result.json"
    
    report = {
        "validation_id": "VAL-FACA-NOGLOB-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        if not data.get("non_global_navigation_confirmed"):
             report["status"] = "fail"
             report["governance_violations"].append("non-globalized navigation verification failed")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_non_globalized_navigation()
    print(json.dumps(res, indent=2))
