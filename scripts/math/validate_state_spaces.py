import json
import os
from datetime import datetime

def validate_state_spaces():
    registry_path = "registry/math/state_space_registry.json"
    result_path = "validation/results/state_space_result.json"
    
    report = {
        "validation_id": "VAL-SS-VALID-001",
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

    # 3. definitions_present
    defs = registry.get("state_space_definitions", [])
    required_symbols = ["x_alpha", "omega_alpha", "R_alpha", "alpha", "CSI_alpha"]
    found_symbols = [d.get("symbol") for d in defs]
    for sym in required_symbols:
        if sym not in found_symbols:
            report["status"] = "fail"
            report["governance_violations"].append(f"symbol_present_{sym}: FAIL")
        else:
            report["checks_passed"].append(f"symbol_present_{sym}")

    # 4. definition_boilerplate_check
    for d in defs:
        sym = d.get("symbol")
        if d.get("source_relation") != "(E≠0) ⇔R δ(E>0)":
            report["status"] = "fail"
            report["governance_violations"].append(f"source_relation_check_{sym}: FAIL")
        else:
            report["checks_passed"].append(f"source_relation_check_{sym}")
        if d.get("non_separability_acknowledged") is not True:
            report["status"] = "fail"
            report["governance_violations"].append(f"non_separability_check_{sym}: FAIL")
        else:
            report["checks_passed"].append(f"non_separability_check_{sym}")

    # 5. hardening_boilerplate_present
    if registry.get("source_relation") != "(E≠0) ⇔R δ(E>0)":
        report["status"] = "fail"
        report["governance_violations"].append("hardening_boilerplate_source_relation: FAIL")
    else:
        report["checks_passed"].append("hardening_boilerplate_source_relation")

    # 6. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "State spaces prove the existence of physical dimensions." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_dimensions_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_dimensions_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_state_spaces()
    print(json.dumps(res, indent=2))
