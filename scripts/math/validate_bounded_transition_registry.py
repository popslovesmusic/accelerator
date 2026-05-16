import json
import os
from datetime import datetime

def validate_bounded_registry():
    registry_path = "registry/math/bounded_local_transition_dynamics_registry.json"
    val_out_path = "validation/results/bounded_transition_validation_result.json"
    
    report = {
        "validation_id": "VAL-BLT-REG-VALID-001",
        "status": "pass",
        "classes_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["classes_verified"] = len(registry["transition_classes"])
        
        # Check for mandatory invariants
        gov = registry["governance"]
        if gov["theorem_status"] != "NOT_PROVEN" or gov["scope_status"] != "STRICTLY_LOCAL_RESTRICTED_DOMAIN":
            report["status"] = "fail"
            report["governance_violations"].append("core governance invariants missing or incorrect in registry")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_bounded_registry()
    print(json.dumps(res, indent=2))
