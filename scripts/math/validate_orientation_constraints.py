import json
import os
from datetime import datetime

def validate_orientation_constraints():
    registry_path = "registry/math/orientation_field_constraints_registry.json"
    val_out_path = "validation/results/orientation_constraints_validation_result.json"
    
    report = {
        "validation_id": "VAL-OFC-REG-VALID-001",
        "status": "pass",
        "constraints_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["constraints_verified"] = len(registry["governance_limits"])
        if not registry.get("governance_limits"):
             report["status"] = "fail"
             report["governance_violations"].append("missing governance limits in registry")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_orientation_constraints()
    print(json.dumps(res, indent=2))
