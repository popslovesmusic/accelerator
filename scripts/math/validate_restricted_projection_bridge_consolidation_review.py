import json
import os
from datetime import datetime

def validate_restricted_projection_bridge_consolidation_review():
    registry_path = "registry/math/restricted_projection_bridge_consolidation_review.json"
    result_path = "validation/results/restricted_projection_bridge_consolidation_review_result.json"
    
    report = {
        "validation_id": "VAL-RPBCR-VALID-001",
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
    
    # 2. review_status_equals_CONSOLIDATION_REVIEW_ONLY
    if status.get("review_status") != "CONSOLIDATION_REVIEW_ONLY":
        report["status"] = "fail"
        report["governance_violations"].append(f"review_status_equals_CONSOLIDATION_REVIEW_ONLY: FAIL (found {status.get('review_status')})")
    else:
        report["checks_passed"].append("review_status_equals_CONSOLIDATION_REVIEW_ONLY")

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

    # 5. forbidden_next_steps_present
    if "forbidden_next_steps" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_next_steps_present: FAIL")
    else:
        report["checks_passed"].append("forbidden_next_steps_present")

    # 6. physics_status_equals_NON_PHYSICAL_ANALOG_MODEL
    if status.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append(f"physics_status_equals_NON_PHYSICAL_ANALOG_MODEL: FAIL (found {status.get('physics_status')})")
    else:
        report["checks_passed"].append("physics_status_equals_NON_PHYSICAL_ANALOG_MODEL")

    # 7. theorem_status_equals_NOT_PROVEN
    if status.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append(f"theorem_status_equals_NOT_PROVEN: FAIL (found {status.get('theorem_status')})")
    else:
        report["checks_passed"].append("theorem_status_equals_NOT_PROVEN")

    # 8. review_result_overall_status_equals_PASS_WITH_WARNINGS
    result = registry.get("review_result", {})
    if result.get("overall_status") != "PASS_WITH_WARNINGS":
         report["status"] = "fail"
         report["governance_violations"].append(f"review_result_overall_status_equals_PASS_WITH_WARNINGS: FAIL (found {result.get('overall_status')})")
    else:
         report["checks_passed"].append("review_result_overall_status_equals_PASS_WITH_WARNINGS")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_restricted_projection_bridge_consolidation_review()
    print(json.dumps(res, indent=2))
