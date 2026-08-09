import json
import os
from datetime import datetime

def validate_bridge_metrics_stress_tests():
    registry_path = "registry/math/bridge_metrics_stress_test_suite.json"
    result_path = "validation/results/bridge_metrics_stress_tests_result.json"
    
    report = {
        "validation_id": "VAL-BMST-VALID-001",
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

    # 3. test_classes_present
    tests = registry.get("test_classes", [])
    required_tests = ["BMST-001", "BMST-002", "BMST-003", "BMST-004", "BMST-005"]
    found_tests = [t.get("test_id") for t in tests]
    for t_id in required_tests:
        if t_id not in found_tests:
            report["status"] = "fail"
            report["governance_violations"].append(f"test_present_{t_id}: FAIL")
        else:
            report["checks_passed"].append(f"test_present_{t_id}")

    # 4. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Stress test passage proves metric infallibility." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_infallibility_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_infallibility_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_bridge_metrics_stress_tests()
    print(json.dumps(res, indent=2))
