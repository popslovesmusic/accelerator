import json
import os
from datetime import datetime

def run_relation_preservation_scrutiny():
    registry_path = "registry/math/relation_preservation_scrutiny.json"
    result_path = "validation/results/relation_preservation_scrutiny_result.json"
    
    report = {
        "validation_id": "VAL-RPS-RUN-001",
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

    # 3. scrutiny_tests_resist_collapse
    tests = registry.get("scrutiny_tests", [])
    all_resisted = all(t.get("result") == "RESISTED" for t in tests)
    if not all_resisted:
        report["status"] = "fail"
        report["governance_violations"].append("relation_preservation_scrutiny: FAIL (some tests allowed collapse)")
    else:
        report["checks_passed"].append("relation_preservation_scrutiny_pass")

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
    res = run_relation_preservation_scrutiny()
    print(json.dumps(res, indent=2))
