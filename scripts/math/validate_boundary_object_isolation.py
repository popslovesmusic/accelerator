import json
import os
from datetime import datetime

def validate_boundary_isolation():
    registry_path = "registry/math/recursive_governance_drift_registry.json"
    result_path = "validation/results/recursive_containment_stress_results.json"
    val_out_path = "validation/results/boundary_object_isolation_validation_result.json"
    
    report = {
        "validation_id": "VAL-RGD-ISO-VALID-001",
        "status": "pass",
        "protected_objects_checked": [],
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        for obj in registry["protected_boundary_objects"]:
            report["protected_objects_checked"].append(obj["object_id"])
            
    # Check if stress test touched protected objects
    if os.path.exists(result_path):
        with open(result_path, 'r') as f:
            stress_data = json.load(f)
            for v in stress_data["vectors_simulated"]:
                if v["protocol"] == "protected_boundary_attack" and v["leakage_detected"]:
                     report["status"] = "fail"
                     report["governance_violations"].append("leakage detected during protected boundary attack")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_boundary_isolation()
    print(json.dumps(res, indent=2))
