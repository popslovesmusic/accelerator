import json
import os
from datetime import datetime

def run_failure_class_survivability_audit():
    registry_path = "registry/math/failure_class_survivability_audit.json"
    result_path = "validation/results/failure_class_survivability_audit_result.json"
    
    report = {
        "validation_id": "VAL-FSA-RUN-001",
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

    # 3. failure_survivability_check
    failures = registry.get("failure_survivability", [])
    all_survived = all(f.get("status") == "SURVIVED" for f in failures)
    if not all_survived:
        report["status"] = "fail"
        report["governance_violations"].append("failure_class_survivability: FAIL (some failures did not survive)")
    else:
        report["checks_passed"].append("failure_class_survivability_pass")

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
    res = run_failure_class_survivability_audit()
    print(json.dumps(res, indent=2))
