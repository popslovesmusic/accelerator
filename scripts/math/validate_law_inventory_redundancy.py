import json
import os
from datetime import datetime

def validate_law_inventory_redundancy():
    registry_path = "registry/math/law_inventory_redundancy_audit.json"
    result_path = "validation/results/law_inventory_redundancy_result.json"
    
    report = {
        "validation_id": "VAL-LRA-VALID-001",
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

    # 3. inventory_coverage_check
    inventory = registry.get("inventory", [])
    if len(inventory) < 34:
        report["status"] = "fail"
        report["governance_violations"].append(f"inventory_coverage: FAIL (found {len(inventory)} laws, expected 34)")
    else:
        report["checks_passed"].append("inventory_coverage_complete")

    # 4. family_assignment_check
    all_assigned = all("candidate_family" in law and law["candidate_family"] is not None for law in inventory)
    if not all_assigned:
        report["status"] = "fail"
        report["governance_violations"].append("family_assignment: FAIL (missing candidate_family in some entries)")
    else:
        report["checks_passed"].append("all_laws_assigned_to_family")

    # 5. audit_checks_verified
    checks = registry.get("audit_checks", {})
    all_verified = all(v == "VERIFIED" for v in checks.values())
    if not all_verified:
        report["status"] = "fail"
        report["governance_violations"].append("audit_checks_verified: FAIL")
    else:
        report["checks_passed"].append("audit_checks_verified")

    # 6. hardening_boilerplate_present
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
    res = validate_law_inventory_redundancy()
    print(json.dumps(res, indent=2))
