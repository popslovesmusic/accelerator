import json
import os
from datetime import datetime

def validate_evolution_constraints():
    registry_path = "registry/math/local_topology_evolution_constraints.json"
    val_out_path = "validation/results/local_topology_constraints_validation_result.json"
    
    report = {
        "validation_id": "VAL-LTEC-REG-VALID-001",
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
        report["constraints_verified"] = len(registry["forbidden_escalations"])
        if not registry.get("forbidden_escalations"):
             report["status"] = "fail"
             report["governance_violations"].append("missing forbidden escalations in registry")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_evolution_constraints()
    print(json.dumps(res, indent=2))
