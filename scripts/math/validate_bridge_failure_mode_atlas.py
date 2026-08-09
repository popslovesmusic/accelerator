import json
import os
from datetime import datetime

def validate_bridge_failure_mode_atlas():
    registry_path = "registry/math/bridge_failure_mode_atlas.json"
    result_path = "validation/results/bridge_failure_mode_atlas_result.json"
    
    report = {
        "validation_id": "VAL-BFMA-VALID-001",
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
    
    # 2. atlas_status_equals_CANDIDATE_BRIDGE_FAILURE_MODE_ATLAS
    if status.get("atlas_status") != "CANDIDATE_BRIDGE_FAILURE_MODE_ATLAS":
        report["status"] = "fail"
        report["governance_violations"].append(f"atlas_status_equals_CANDIDATE_BRIDGE_FAILURE_MODE_ATLAS: FAIL (found {status.get('atlas_status')})")
    else:
        report["checks_passed"].append("atlas_status_equals_CANDIDATE_BRIDGE_FAILURE_MODE_ATLAS")

    # 3. failure_mode_classes_present
    classes = registry.get("failure_mode_classes", [])
    if not classes:
        report["status"] = "fail"
        report["governance_violations"].append("failure_mode_classes_present: FAIL")
    else:
        report["checks_passed"].append("failure_mode_classes_present")

    # 4. failure_modes_include_required
    class_names = [c.get("name") for c in classes]
    required_names = [
        "false_unification",
        "category_confusion",
        "projection_identity_error",
        "loss_differential_overreading",
        "physical_law_escalation"
    ]
    missing_names = [rn for rn in required_names if rn not in class_names]
    if missing_names:
        report["status"] = "fail"
        report["governance_violations"].append(f"failure_modes_include_required: FAIL (missing {missing_names})")
    else:
        report["checks_passed"].append("failure_modes_include_required")

    # 5. failure_record_schema_present
    if "failure_record_schema" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("failure_record_schema_present: FAIL")
    else:
        report["checks_passed"].append("failure_record_schema_present")

    # 6. mitigation_rules_present
    if "mitigation_rules" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("mitigation_rules_present: FAIL")
    else:
        report["checks_passed"].append("mitigation_rules_present")

    # 7. physics_status_equals_NON_PHYSICAL_ANALOG_MODEL
    if status.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append(f"physics_status_equals_NON_PHYSICAL_ANALOG_MODEL: FAIL (found {status.get('physics_status')})")
    else:
        report["checks_passed"].append("physics_status_equals_NON_PHYSICAL_ANALOG_MODEL")

    # 8. theorem_status_equals_NOT_PROVEN
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
    res = validate_bridge_failure_mode_atlas()
    print(json.dumps(res, indent=2))
