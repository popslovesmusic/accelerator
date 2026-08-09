import json
import os
from datetime import datetime

def validate_embedded_observer_dynamics():
    registry_path = "registry/math/embedded_observer_dynamics_registry.json"
    result_path = "validation/results/embedded_observer_dynamics_result.json"
    
    report = {
        "validation_id": "VAL-EOD-VALID-001",
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

    # 3. dynamic_constraints_present
    constraints = registry.get("dynamic_constraints", [])
    required_constraints = ["observer_trace_feedback", "measurement_deformation", "tool_generated_projection_shift", "recursive_reference_amplification", "embedded_accessibility_decay"]
    found_constraints = [c.get("constraint_id") for c in constraints]
    for c_id in required_constraints:
        if c_id not in found_constraints:
            report["status"] = "fail"
            report["governance_violations"].append(f"constraint_present_{c_id}: FAIL")
        else:
            report["checks_passed"].append(f"constraint_present_{c_id}")

    # 4. dynamic_bounds_present
    bounds = registry.get("dynamic_bounds", [])
    required_bounds = ["EOD_LOCAL_FEEDBACK_ONLY", "EOD_PARTIAL_TRACE_LOCK", "EOD_CONFLICT_DEPENDENT", "EOD_EXTERNALITY_FORBIDDEN"]
    found_bounds = [b.get("bound_id") for b in bounds]
    for b_id in required_bounds:
        if b_id not in found_bounds:
            report["status"] = "fail"
            report["governance_violations"].append(f"bound_present_{b_id}: FAIL")
        else:
            report["checks_passed"].append(f"bound_present_{b_id}")

    # 5. hardening_boilerplate_present
    if registry.get("source_relation") != "(E≠0) ⇔R δ(E>0)":
        report["status"] = "fail"
        report["governance_violations"].append("hardening_boilerplate_source_relation: FAIL")
    else:
        report["checks_passed"].append("hardening_boilerplate_source_relation")

    # 6. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Embedded observers can achieve detached dynamic analysis." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_detachment_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_detachment_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_embedded_observer_dynamics()
    print(json.dumps(res, indent=2))
