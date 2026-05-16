import json
import os
from datetime import datetime

def validate_embedded_observer_constraints():
    registry_path = "registry/math/embedded_observer_constraints_registry.json"
    result_path = "validation/results/embedded_observer_constraints_result.json"
    
    report = {
        "validation_id": "VAL-EO-VALID-001",
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

    # 3. observer_constraints_present
    constraints = registry.get("observer_constraints", [])
    required_constraints = ["no_complete_externality", "bounded_self_description", "observer_generated_tooling_constraint", "recursive_measurement_limit", "internal_reference_dependence"]
    found_constraints = [c.get("constraint_id") for c in constraints]
    for c_id in required_constraints:
        if c_id not in found_constraints:
            report["status"] = "fail"
            report["governance_violations"].append(f"constraint_present_{c_id}: FAIL")
        else:
            report["checks_passed"].append(f"constraint_present_{c_id}")

    # 4. accessibility_bounds_present
    bounds = registry.get("accessibility_bounds", [])
    required_bounds = ["EOA_LOCAL_ONLY", "EOA_PARTIAL_RECONSTRUCTION", "EOA_CONFLICT_LOCKED", "EOA_EXTERNALITY_BLOCKED"]
    found_bounds = [b.get("bound_id") for b in bounds]
    for b_id in required_bounds:
        if b_id not in found_bounds:
            report["status"] = "fail"
            report["governance_violations"].append(f"bound_present_{b_id}: FAIL")
        else:
            report["checks_passed"].append(f"bound_present_{b_id}")

    # 5. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Embedded observers can prove the full source relation." not in forbidden:
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
    res = validate_embedded_observer_constraints()
    print(json.dumps(res, indent=2))
