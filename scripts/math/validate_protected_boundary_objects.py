import json
import os
from datetime import datetime

def validate_boundary_objects():
    registry_path = "registry/math/recursive_governance_drift_registry.json"
    result_path = "validation/results/protected_boundary_objects_validation_result.json"
    
    report = {
        "validation_id": "VAL-RGD-BOUND-VALID-001",
        "status": "pass",
        "protected_objects": [],
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing drift registry")
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        for obj in registry["protected_boundary_objects"]:
            report["protected_objects"].append(obj["object_id"])
            # Check for mandatory restrictions
            if not obj.get("restrictions"):
                 report["status"] = "fail"
                 report["governance_violations"].append(f"missing restrictions for protected object {obj['object_id']}")

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_boundary_objects()
    print(json.dumps(res, indent=2))
