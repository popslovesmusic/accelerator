import json
import os
from datetime import datetime

def validate_bridge_stress_test_scaffold():
    registry_path = "registry/math/bridge_stress_test_scaffold.json"
    result_path = "validation/results/bridge_stress_test_scaffold_result.json"
    
    report = {
        "validation_id": "VAL-BSTS-VALID-001",
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
        
    status = registry.get("status", {})
    
    # 2. scaffold_status_equals_CANDIDATE_BRIDGE_STRESS_TEST_SCAFFOLD
    if status.get("scaffold_status") != "CANDIDATE_BRIDGE_STRESS_TEST_SCAFFOLD":
        report["status"] = "fail"
        report["governance_violations"].append(f"scaffold_status_equals_CANDIDATE_BRIDGE_STRESS_TEST_SCAFFOLD: FAIL (found {status.get('scaffold_status')})")
    else:
        report["checks_passed"].append("scaffold_status_equals_CANDIDATE_BRIDGE_STRESS_TEST_SCAFFOLD")

    # 3. stress_test_classes_include_BST001_to_BST005
    classes = registry.get("stress_test_classes", [])
    class_ids = [c.get("test_id") for c in classes]
    required_ids = [f"BST-{str(i).zfill(3)}" for i in range(1, 6)]
    missing_ids = [ri for ri in required_ids if ri not in class_ids]
    if missing_ids:
        report["status"] = "fail"
        report["governance_violations"].append(f"stress_test_classes_include_BST001_to_BST005: FAIL (missing {missing_ids})")
    else:
        report["checks_passed"].append("stress_test_classes_include_BST001_to_BST005")

    # 4. stress_test_record_schema_present
    if "stress_test_record_schema" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("stress_test_record_schema_present: FAIL")
    else:
        report["checks_passed"].append("stress_test_record_schema_present")

    # 5. required_test_behaviors_present
    if "required_test_behaviors" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("required_test_behaviors_present: FAIL")
    else:
        report["checks_passed"].append("required_test_behaviors_present")

    # 6-7. forbidden_outcomes checks
    forbidden = registry.get("forbidden_outcomes", [])
    required_forbidden = [
        ("Unification claim accepted.", "forbidden_outcomes_include_unification_claim_accepted"),
        ("Physical derivation claim accepted.", "forbidden_outcomes_include_physical_derivation_claim_accepted")
    ]
    for outcome, check_name in required_forbidden:
        if outcome not in forbidden:
            report["status"] = "fail"
            report["governance_violations"].append(f"{check_name}: FAIL (missing '{outcome}')")
        else:
            report["checks_passed"].append(check_name)

    # 8. physics_status_equals_NON_PHYSICAL_ANALOG_MODEL
    if status.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append(f"physics_status_equals_NON_PHYSICAL_ANALOG_MODEL: FAIL (found {status.get('physics_status')})")
    else:
        report["checks_passed"].append("physics_status_equals_NON_PHYSICAL_ANALOG_MODEL")

    # 9. theorem_status_equals_NOT_PROVEN
    if status.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append(f"theorem_status_equals_NOT_PROVEN: FAIL (found {status.get('theorem_status')})")
    else:
        report["checks_passed"].append("theorem_status_equals_NOT_PROVEN")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_bridge_stress_test_scaffold()
    print(json.dumps(res, indent=2))
