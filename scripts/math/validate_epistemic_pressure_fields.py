import json
import os
from datetime import datetime

def validate_pressure_fields():
    registry_path = "registry/math/ecological_pressure_field_registry.json"
    val_out_path = "validation/results/epistemic_pressure_fields_validation_result.json"
    
    report = {
        "validation_id": "VAL-EPF-REG-VALID-001",
        "status": "pass",
        "fields_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["fields_verified"] = len(registry["pressure_fields"])
        if not registry.get("pressure_fields"):
             report["status"] = "fail"
             report["governance_violations"].append("missing pressure fields in registry")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_pressure_fields()
    print(json.dumps(res, indent=2))
