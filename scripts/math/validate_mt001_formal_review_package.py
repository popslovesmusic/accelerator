import json
import os
from datetime import datetime

def validate_mt001_formal_review_package():
    registry_path = "registry/math/mt001_formal_review_package.json"
    result_path = "validation/results/mt001_formal_review_package_result.json"
    
    report = {
        "validation_id": "VAL-MT001-PK-VALID-001",
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

    # 3. contents_present
    contents = registry.get("package_contents", [])
    required_contents = ["formal_statement", "proof_skeleton", "explicit_assumptions", "counterexample_boundaries"]
    for item in required_contents:
        if item not in contents:
            report["status"] = "fail"
            report["governance_violations"].append(f"content_missing_{item}: FAIL")
        else:
            report["checks_passed"].append(f"content_present_{item}")

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
    res = validate_mt001_formal_review_package()
    print(json.dumps(res, indent=2))
