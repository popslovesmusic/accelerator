import json
import os
from datetime import datetime

def validate_boundary_object():
    result_path = "validation/results/restricted_local_topology_restart_results.json"
    val_out_path = "validation/results/boundary_object_protection_validation_result.json"
    
    report = {
        "validation_id": "VAL-RLT-OBJ-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        if not data.get("boundary_load_monitored"):
             report["status"] = "fail"
             report["governance_violations"].append("boundary load monitoring failed")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_boundary_object()
    print(json.dumps(res, indent=2))
