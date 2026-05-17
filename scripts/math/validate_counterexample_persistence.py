import json
import os
from datetime import datetime

def validate_counterexample_persistence():
    registry_path = "registry/math/counterexample_persistence_audit.json"
    result_path = "validation/results/counterexample_persistence_result.json"
    
    report = {
        "validation_id": "VAL-CPA-VALID-001",
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

    # 3. mandatory_checks_present
    checks = registry.get("mandatory_checks", [])
    required_ids = ["projection_non_idempotence_preserved", "orientation_locking_preserved", "empty_admissible_image_preserved"]
    found_ids = [c.get("check_id") for c in checks]
    for c_id in required_ids:
        if c_id not in found_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"check_present_{c_id}: FAIL")
        else:
            report["checks_passed"].append(f"check_present_{c_id}")

    # 4. checks_verified
    for c in checks:
        if c.get("status") != "VERIFIED":
            report["status"] = "fail"
            report["governance_violations"].append(f"check_not_verified_{c.get('check_id')}: FAIL")
        else:
            report["checks_passed"].append(f"check_verified_{c.get('check_id')}")

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
    res = validate_counterexample_persistence()
    print(json.dumps(res, indent=2))
