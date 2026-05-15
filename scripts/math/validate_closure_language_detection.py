import json
import os
from datetime import datetime

def validate_closure_detection():
    registry_path = "registry/math/recursive_governance_drift_registry.json"
    result_path = "validation/results/closure_language_detection_validation_result.json"
    
    report = {
        "validation_id": "VAL-RGD-LANG-VALID-001",
        "status": "pass",
        "patterns_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing drift registry")
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["patterns_verified"] = len(registry["closure_language_patterns"])
        if not registry.get("closure_language_patterns"):
             report["status"] = "fail"
             report["governance_violations"].append("missing closure language patterns in registry")

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_closure_detection()
    print(json.dumps(res, indent=2))
