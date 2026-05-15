import json
import os
from datetime import datetime

def validate_quarantine_integrity():
    result_path = "validation/results/recursive_containment_stress_results.json"
    val_out_path = "validation/results/quarantine_integrity_validation_result.json"
    
    report = {
        "validation_id": "VAL-RCS-QUAR-VALID-001",
        "status": "pass",
        "integrity_score": 0.0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        report["integrity_score"] = data["quarantine_integrity_score"]
        
        if report["integrity_score"] < 0.8:
             report["status"] = "fail"
             report["governance_violations"].append("quarantine integrity score below critical threshold")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_quarantine_integrity()
    print(json.dumps(res, indent=2))
