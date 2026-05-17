import json
import os
from datetime import datetime

def validate_restricted_derivability_classification():
    registry_path = "registry/math/restricted_derivability_classification.json"
    result_path = "validation/results/restricted_derivability_classification_result.json"
    
    report = {
        "validation_id": "VAL-RDC-VALID-001",
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

    # 3. classification_levels_present
    levels = registry.get("classification_levels", [])
    required_ids = ["NOT_CONSTRUCTED", "COUNTEREXAMPLE_ACTIVE", "LOCALLY_DERIVABLE_UNDER_ASSUMPTIONS", "READY_FOR_PEER_REVIEW_PREPARATION"]
    found_ids = [l.get("level_id") for l in levels]
    for l_id in required_ids:
        if l_id not in found_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"level_present_{l_id}: FAIL")
        else:
            report["checks_passed"].append(f"level_present_{l_id}")

    # 4. forbidden_levels_present
    forbidden = registry.get("forbidden_levels", [])
    required_f_ids = ["GLOBALLY_PROVEN", "PHYSICALLY_CONFIRMED"]
    found_f_ids = [f.get("level_id") for f in forbidden]
    for f_id in required_f_ids:
        if f_id not in found_f_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"forbidden_level_present_{f_id}: FAIL")
        else:
            report["checks_passed"].append(f"forbidden_level_present_{f_id}")

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
    res = validate_restricted_derivability_classification()
    print(json.dumps(res, indent=2))
