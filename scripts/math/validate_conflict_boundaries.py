import json
import os
from datetime import datetime

def validate_conflict_boundaries():
    registry_path = "registry/math/conflict_boundary_registry.json"
    result_path = "validation/results/conflict_boundary_result.json"
    
    report = {
        "validation_id": "VAL-CB-VALID-001",
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

    # 3. conflict_classes_present
    classes = registry.get("conflict_classes", [])
    required_classes = ["DISCRETE_CONTINUOUS_CONFLICT", "LOCAL_GLOBAL_CONFLICT", "THRESHOLD_FLOW_CONFLICT", "PARTICIPATORY_GEOMETRIC_CONFLICT", "EMBEDDED_EXTERNALITY_CONFLICT"]
    found_classes = [c.get("class_id") for c in classes]
    for c_id in required_classes:
        if c_id not in found_classes:
            report["status"] = "fail"
            report["governance_violations"].append(f"class_present_{c_id}: FAIL")
        else:
            report["checks_passed"].append(f"class_present_{c_id}")

    # 4. governance_rules_present
    rules = registry.get("governance_rules", [])
    if len(rules) < 3:
        report["status"] = "fail"
        report["governance_violations"].append("governance_rules_present: FAIL (insufficient count)")
    else:
        report["checks_passed"].append("governance_rules_present")

    # 5. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Reconstruction topology resolves the discrete/continuous conflict." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_resolution_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_resolution_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_conflict_boundaries()
    print(json.dumps(res, indent=2))
