import json
import os
from datetime import datetime

def validate_failure_geometry_reorganization():
    result_path = "validation/results/local_constraint_reconfiguration_results.json"
    val_out_path = "validation/results/failure_geometry_reorganization_validation_result.json"
    
    report = {
        "validation_id": "VAL-LCR-GEOM-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        if not data.get("reconfigurations_mapped"):
             report["status"] = "fail"
             report["governance_violations"].append("no reconfigurations mapped in results")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_failure_geometry_reorganization()
    print(json.dumps(res, indent=2))
