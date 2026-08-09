import json
import os
from datetime import datetime

def validate_law_consolidation_final_audit():
    registry_path = "registry/math/law_consolidation_final_audit.json"
    result_path = "validation/results/law_consolidation_final_audit_result.json"
    
    report = {
        "validation_id": "VAL-LCFA-VALID-001",
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

    # 3. audit_findings_present
    if "audit_findings" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("audit_findings_present: FAIL")
    else:
        report["checks_passed"].append("audit_findings_present")

    # 4. audit_result_present
    result = registry.get("audit_result", {})
    if result.get("overall_status") != "CONSOLIDATION_PASS":
        report["status"] = "fail"
        report["governance_violations"].append(f"audit_result_status: FAIL (found {result.get('overall_status')})")
    else:
        report["checks_passed"].append("audit_result_status_pass")

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
    res = validate_law_consolidation_final_audit()
    print(json.dumps(res, indent=2))
