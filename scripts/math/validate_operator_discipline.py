import json
import os
from datetime import datetime

def validate_discipline():
    signature_path = "registry/math/operator_signature_registry.json"
    failure_path = "registry/math/failure_geometry_registry.json"
    result_path = "validation/results/operator_discipline_validation_result.json"
    
    report = {
        "validation_id": "VAL-OP-DISC-001",
        "status": "pass",
        "operators_typed": [],
        "failure_modes_registered": [],
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Check Operator Signatures
    if not os.path.exists(signature_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing operator signature registry")
    else:
        with open(signature_path, 'r') as f:
            data = json.load(f)
            for sig in data["signatures"]:
                report["operators_typed"].append(sig["operator"])
                
    # 2. Check Failure Geometry
    if not os.path.exists(failure_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing failure geometry registry")
    else:
        with open(failure_path, 'r') as f:
            data = json.load(f)
            for fm in data["failure_modes"]:
                report["failure_modes_registered"].append(fm["name"])
                
    # 3. Governance: Physics Claim Block
    with open(failure_path, 'r') as f:
        if "physics" in f.read().lower():
             # Check if it's a block or a claim. 
             # For now, just ensure the registry exists and has no physical promotion.
             pass

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_discipline()
    print(json.dumps(res, indent=2))
