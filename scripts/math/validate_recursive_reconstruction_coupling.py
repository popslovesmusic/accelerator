import json
import os
from datetime import datetime

def validate_recursive_reconstruction_coupling():
    registry_path = "registry/math/recursive_reconstruction_coupling_registry.json"
    result_path = "validation/results/recursive_reconstruction_coupling_result.json"
    
    report = {
        "validation_id": "VAL-RRC-VALID-001",
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

    # 3. coupling_classes_present
    classes = registry.get("coupling_classes", [])
    required_classes = ["RRC_PARTIAL_ALIGNMENT", "RRC_CONFLICT_PRESERVING", "RRC_TRACE_REINFORCING", "RRC_DRIFT_AMPLIFYING", "RRC_COLLAPSE_TRIGGERING"]
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

    # 6. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Recursive coupling proves that the system is 'self-aware'." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_self_aware_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_self_aware_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_recursive_reconstruction_coupling()
    print(json.dumps(res, indent=2))
