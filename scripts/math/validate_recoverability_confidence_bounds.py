import json
import os
from datetime import datetime

def validate_recoverability_confidence_bounds():
    registry_path = "registry/math/recoverability_confidence_bounds.json"
    result_path = "validation/results/recoverability_confidence_bounds_result.json"
    
    report = {
        "validation_id": "VAL-RCB-VALID-001",
        "status": "pass",
        "checks_passed": [],
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. registry_exists
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("registry_exists: FAIL (registry missing)")
        return report
    report["checks_passed"].append("registry_exists")

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    gov = registry.get("governance_status", {})
    
    # 2. physics_status_equals_NON_PHYSICAL_ANALOG_MODEL
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append(f"physics_status_equals_NON_PHYSICAL_ANALOG_MODEL: FAIL (found {gov.get('physics_status')})")
    else:
        report["checks_passed"].append("physics_status_equals_NON_PHYSICAL_ANALOG_MODEL")

    # 3. confidence_bounds_present
    bounds = registry.get("confidence_bounds", [])
    required_bounds = ["RCOV_CONF_0", "RCOV_CONF_1", "RCOV_CONF_2", "RCOV_CONF_3"]
    found_bounds = [b.get("bound_id") for b in bounds]
    for b_id in required_bounds:
        if b_id not in found_bounds:
            report["status"] = "fail"
            report["governance_violations"].append(f"bound_present_{b_id}: FAIL")
        else:
            report["checks_passed"].append(f"bound_present_{b_id}")

    # 4. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Projected forms reconstruct ⇔R by themselves." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_reconstruction_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_reconstruction_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_recoverability_confidence_bounds()
    print(json.dumps(res, indent=2))
