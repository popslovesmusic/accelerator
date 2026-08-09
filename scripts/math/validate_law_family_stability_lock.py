import json
import os
from datetime import datetime

def validate_law_family_stability_lock():
    registry_path = "registry/math/law_family_stability_lock.json"
    result_path = "validation/results/law_family_stability_lock_result.json"
    
    report = {
        "validation_id": "VAL-LFL-VALID-001",
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

    # 3. all_families_locked
    families = registry.get("authoritative_family_set", [])
    if len(families) != 7:
        report["status"] = "fail"
        report["governance_violations"].append(f"authoritative_set_count: FAIL (found {len(families)}, expected 7)")
    else:
        report["checks_passed"].append("authoritative_set_count_pass")
        
    all_locked = all(f.get("lock_status") == "LOCKED" for f in families)
    if not all_locked:
        report["status"] = "fail"
        report["governance_violations"].append("family_lock_status: FAIL (some families not LOCKED)")
    else:
        report["checks_passed"].append("family_lock_status_pass")

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
    res = validate_law_family_stability_lock()
    print(json.dumps(res, indent=2))
