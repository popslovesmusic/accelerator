import json
import os
from datetime import datetime

def validate_proof_skeletons():
    registry_path = "registry/math/proof_skeleton_registry.json"
    result_path = "validation/results/proof_skeleton_result.json"
    
    report = {
        "validation_id": "VAL-SKEL-VALID-001",
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

    # 3. skeletons_present
    skeletons = registry.get("proof_skeletons", [])
    required_targets = ["MT-001", "MT-002", "MT-003"]
    found_targets = [s.get("target_theorem") for s in skeletons]
    for target in required_targets:
        if target not in found_targets:
            report["status"] = "fail"
            report["governance_violations"].append(f"skeleton_present_{target}: FAIL")
        else:
            report["checks_passed"].append(f"skeleton_present_{target}")

    # 4. skeleton_fields_check
    for s in skeletons:
        target = s.get("target_theorem")
        required_fields = ["declared_assumptions", "dependency_chain", "proof_steps", "failure_exposure_points"]
        for field in required_fields:
            if field not in s:
                report["status"] = "fail"
                report["governance_violations"].append(f"skeleton_field_missing_{target}_{field}: FAIL")
            else:
                report["checks_passed"].append(f"skeleton_field_present_{target}_{field}")

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
    res = validate_proof_skeletons()
    print(json.dumps(res, indent=2))
