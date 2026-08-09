import json
import os
from datetime import datetime

def validate_resumption_gate():
    registry_path = "registry/math/governed_resumption_readiness_gate.json"
    val_out_path = "validation/results/governed_resumption_readiness_validation_result.json"
    
    report = {
        "validation_id": "VAL-GRR-REG-VALID-001",
        "status": "pass",
        "checks_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["checks_verified"] = len(registry["readiness_checks"])
        
        # Check for mandatory invariants
        gov = registry["governance"]
        if gov["theorem_status"] != "NOT_PROVEN" or gov["scope_status"] != "STRICTLY_LOCAL_RESTRICTED_DOMAIN":
            report["status"] = "fail"
            report["governance_violations"].append("core governance invariants missing or incorrect in gate registry")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_resumption_gate()
    print(json.dumps(res, indent=2))
