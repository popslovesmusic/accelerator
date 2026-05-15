import json
import os
from datetime import datetime

def validate_preservation_policy():
    registry_path = "registry/math/irreducible_preservation_policy_registry.json"
    val_out_path = "validation/results/irreducible_preservation_policy_validation_result.json"
    
    report = {
        "validation_id": "VAL-IPP-REG-VALID-001",
        "status": "pass",
        "modes_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["modes_verified"] = len(registry["preservation_modes"])
        if not registry.get("preservation_modes"):
             report["status"] = "fail"
             report["governance_violations"].append("missing preservation modes in registry")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_preservation_policy()
    print(json.dumps(res, indent=2))
