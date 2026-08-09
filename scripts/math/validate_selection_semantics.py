import json
import os
from datetime import datetime

def validate_selection_semantics():
    registry_path = "registry/math/selection_semantics_registry.json"
    result_path = "validation/results/selection_semantics_result.json"
    
    report = {
        "validation_id": "VAL-SEL-VALID-001",
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

    # 3. semantics_classes_present
    classes = registry.get("selection_semantics_classes", [])
    required_ids = ["DELTA_RELATIONAL", "DELTA_PARTIAL_FUNCTION_UNDER_RULE", "DELTA_UNDEFINED_ON_FAILURE"]
    found_ids = [c.get("class_id") for c in classes]
    for c_id in required_ids:
        if c_id not in found_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"class_present_{c_id}: FAIL")
        else:
            report["checks_passed"].append(f"class_present_{c_id}")

    # 4. required_policies_present
    policies = registry.get("required_policies", [])
    required_p_ids = ["degeneracy_handling", "tie_breaking_policy", "empty_image_policy"]
    found_p_ids = [p.get("policy_id") for p in policies]
    for p_id in required_p_ids:
        if p_id not in found_p_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"policy_present_{p_id}: FAIL")
        else:
            report["checks_passed"].append(f"policy_present_{p_id}")

    # 5. hardening_boilerplate_present
    if registry.get("source_relation") != "(E≠0) ⇔R δ(E>0)":
        report["status"] = "fail"
        report["governance_violations"].append("hardening_boilerplate_source_relation: FAIL")
    else:
        report["checks_passed"].append("hardening_boilerplate_source_relation")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_selection_semantics()
    print(json.dumps(res, indent=2))
