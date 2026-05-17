import json
import os
from datetime import datetime

def validate_recursive_semantic_reference():
    registry_path = "registry/math/recursive_semantic_reference_registry.json"
    result_path = "validation/results/recursive_semantic_reference_result.json"
    
    report = {
        "validation_id": "VAL-RSR-VALID-001",
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

    # 3. reference_classes_present
    classes = registry.get("reference_classes", [])
    required_classes = ["RSR_PARTIAL_SELF_TRACE", "RSR_FEEDBACK_BOUND", "RSR_CONFLICT_STABILIZED", "RSR_RECURSIVE_DRIFT", "RSR_CLOSURE_BLOCKED"]
    found_classes = [c.get("class_id") for c in classes]
    for c_id in required_classes:
        if c_id not in found_classes:
            report["status"] = "fail"
            report["governance_violations"].append(f"class_present_{c_id}: FAIL")
        else:
            report["checks_passed"].append(f"class_present_{c_id}")

    # 4. mandatory_constraints_present
    constraints = registry.get("mandatory_constraints", [])
    if len(constraints) < 3:
        report["status"] = "fail"
        report["governance_violations"].append("mandatory_constraints_present: FAIL (insufficient count)")
    else:
        report["checks_passed"].append("mandatory_constraints_present")

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
    res = validate_recursive_semantic_reference()
    print(json.dumps(res, indent=2))
