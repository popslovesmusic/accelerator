import json
import os
from datetime import datetime

def validate_topology():
    registry_path = "registry/math/boundary_interaction_topology_registry.json"
    val_out_path = "validation/results/boundary_interaction_topology_validation_result.json"
    
    report = {
        "validation_id": "VAL-BIT-REG-VALID-001",
        "status": "pass",
        "types_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["types_verified"] = len(registry["interaction_types"])
        if not registry.get("interaction_types"):
             report["status"] = "fail"
             report["governance_violations"].append("missing interaction types in registry")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_topology()
    print(json.dumps(res, indent=2))
