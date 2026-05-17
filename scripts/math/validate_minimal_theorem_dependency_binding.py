import json
import os
from datetime import datetime

def validate_minimal_theorem_dependency_binding():
    registry_path = "registry/math/minimal_theorem_dependency_binding.json"
    result_path = "validation/results/minimal_theorem_dependency_binding_result.json"
    
    report = {
        "validation_id": "VAL-TDB-VALID-001",
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

    # 3. bindings_present
    bindings = registry.get("theorem_bindings", [])
    required_ids = ["MT-001", "MT-002", "MT-003"]
    found_ids = [b.get("theorem_id") for b in bindings]
    for b_id in required_ids:
        if b_id not in found_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"binding_present_{b_id}: FAIL")
        else:
            report["checks_passed"].append(f"binding_present_{b_id}")

    # 4. hardening_boilerplate_present
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
    res = validate_minimal_theorem_dependency_binding()
    print(json.dumps(res, indent=2))
