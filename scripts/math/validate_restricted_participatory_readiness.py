import json
import os
from datetime import datetime

def validate_restricted_participatory_readiness():
    registry_path = "registry/math/restricted_participatory_readiness_audit.json"
    result_path = "validation/results/restricted_participatory_readiness_result.json"
    
    report = {
        "validation_id": "VAL-PRA-REG-VALID-001",
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

    # 3. readiness_checks_pass
    checks = registry.get("readiness_checks", [])
    all_pass = all(c.get("status") == "PASS" for c in checks)
    if not all_pass:
        report["status"] = "fail"
        report["governance_violations"].append("readiness_checks: FAIL (not all checks passed)")
    else:
        report["checks_passed"].append("readiness_checks_pass")

    # 4. result_ready
    res = registry.get("audit_result", {})
    if res.get("overall_readiness") != "READY_FOR_RESTRICTED_DISCUSSION":
        report["status"] = "fail"
        report["governance_violations"].append(f"readiness_status: FAIL (found {res.get('overall_readiness')})")
    else:
        report["checks_passed"].append("readiness_status_pass")

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
    res = validate_restricted_participatory_readiness()
    print(json.dumps(res, indent=2))
