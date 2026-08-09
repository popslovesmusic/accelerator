import json
import os
from datetime import datetime

def validate_restricted_proof_strength_classification():
    registry_path = "registry/math/restricted_proof_strength_classification.json"
    result_path = "validation/results/restricted_proof_strength_classification_result.json"
    
    report = {
        "validation_id": "VAL-PSC-VALID-001",
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
    required_ids = ["NOT_REVIEWED", "REVIEW_BLOCKED", "COUNTEREXAMPLE_ACTIVE", "SUPPORTED_UNDER_ASSUMPTIONS", "LOCAL_PROOF_CANDIDATE", "READY_FOR_FORMAL_PROOF_REVIEW"]
    found_ids = [l.get("level_id") for l in levels]
    for l_id in required_ids:
        if l_id not in found_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"level_present_{l_id}: FAIL")
        else:
            report["checks_passed"].append(f"level_present_{l_id}")

    # 4. forbidden_escalations_present
    esc = registry.get("forbidden_escalations", [])
    required_esc = ["PROVEN", "PHYSICALLY_VALIDATED", "GLOBAL_THEOREM", "UNIFICATION_SUPPORT"]
    found_esc = [e.get("target_status") for e in esc]
    for e_id in required_esc:
        if e_id not in found_esc:
            report["status"] = "fail"
            report["governance_violations"].append(f"escalation_blocked_{e_id}: FAIL")
        else:
            report["checks_passed"].append(f"escalation_blocked_{e_id}")

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
    res = validate_restricted_proof_strength_classification()
    print(json.dumps(res, indent=2))
