import json
import os
from datetime import datetime

def validate_minimal_framework_canonicalization():
    registry_path = "registry/math/minimal_framework_canonicalization.json"
    result_path = "validation/results/minimal_framework_canonicalization_result.json"
    
    report = {
        "validation_id": "VAL-MFC-VALID-001",
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

    # 3. canonical_profile_complete
    profile = registry.get("canonical_profile", {})
    required_keys = ["authoritative_operators", "authoritative_law_families", "authoritative_failure_families", "minimal_assumption_core", "irreducible_relation_statement"]
    for key in required_keys:
        if key not in profile or not profile[key]:
            report["status"] = "fail"
            report["governance_violations"].append(f"canonical_profile_missing_{key}: FAIL")
        else:
            report["checks_passed"].append(f"canonical_profile_present_{key}")

    # 4. relation_statement_check
    stmt = profile.get("irreducible_relation_statement", "")
    if "relation ⇔R, not its aspects" not in stmt:
        report["status"] = "fail"
        report["governance_violations"].append("relation_statement_integrity: FAIL")
    else:
        report["checks_passed"].append("relation_statement_integrity_pass")

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
    res = validate_minimal_framework_canonicalization()
    print(json.dumps(res, indent=2))
