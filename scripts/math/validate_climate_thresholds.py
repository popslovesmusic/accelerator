import json
import os
from datetime import datetime

def validate_thresholds():
    registry_path = "registry/math/epistemic_climate_thresholds.json"
    val_out_path = "validation/results/epistemic_climate_thresholds_validation_result.json"
    
    report = {
        "validation_id": "VAL-ECT-REG-VALID-001",
        "status": "pass",
        "thresholds_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["thresholds_verified"] = len(registry["threshold_classes"])
        if not registry.get("threshold_classes"):
             report["status"] = "fail"
             report["governance_violations"].append("missing threshold classes in registry")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_thresholds()
    print(json.dumps(res, indent=2))
