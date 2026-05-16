import json
import os
from datetime import datetime

def validate_reconstruction_topology_consolidation():
    registry_path = "registry/math/reconstruction_topology_consolidation_review.json"
    result_path = "validation/results/reconstruction_topology_consolidation_result.json"
    
    report = {
        "validation_id": "VAL-RTC-VALID-001",
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

    # 3. review_findings_present
    if "review_findings" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("review_findings_present: FAIL")
    else:
        report["checks_passed"].append("review_findings_present")

    # 4. review_result_present
    if "review_result" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("review_result_present: FAIL")
    else:
        report["checks_passed"].append("review_result_present")

    # 5. forbidden_next_steps checks
    forbidden = registry.get("forbidden_next_steps", [])
    if "Claiming reconstruction topology proves source identity." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_next_steps_include_unification_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_next_steps_include_unification_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_reconstruction_topology_consolidation()
    print(json.dumps(res, indent=2))
