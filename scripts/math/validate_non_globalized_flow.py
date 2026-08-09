import json
import os
from datetime import datetime

def validate_non_globalized_flow():
    result_path = "validation/results/constraint_flow_coherence_report.json"
    val_out_path = "validation/results/non_globalized_flow_validation_result.json"
    
    report = {
        "validation_id": "VAL-BCF-NOGLOB-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        if not data.get("non_global_stability_confirmed"):
             report["status"] = "fail"
             report["governance_violations"].append("non-globalized flow verification failed")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_non_globalized_flow()
    print(json.dumps(res, indent=2))
