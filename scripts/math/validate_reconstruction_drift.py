import json
import os
from datetime import datetime

def validate_reconstruction_drift():
    registry_path = "registry/math/reconstruction_drift_registry.json"
    result_path = "validation/results/reconstruction_drift_result.json"
    
    report = {
        "validation_id": "VAL-RD-VALID-001",
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

    # 3. drift_flags_present
    flags = registry.get("drift_flags", [])
    required_flags = ["source_identity_drift", "topology_realism_drift", "hidden_reversibility_drift", "unification_language_drift", "projection_collapse_drift", "observer_detachment_drift"]
    found_flags = [f.get("flag_id") for f in flags]
    for f_id in required_flags:
        if f_id not in found_flags:
            report["status"] = "fail"
            report["governance_violations"].append(f"flag_present_{f_id}: FAIL")
        else:
            report["checks_passed"].append(f"flag_present_{f_id}")

    # 4. automatic_review_triggers_present
    triggers = registry.get("automatic_review_triggers", [])
    required_triggers = ["recoverability_equals_identity", "conflict_removed", "external_viewpoint_assumed", "projection_loss_omitted"]
    found_triggers = [t.get("trigger_id") for t in triggers]
    for t_id in required_triggers:
        if t_id not in found_triggers:
            report["status"] = "fail"
            report["governance_violations"].append(f"trigger_present_{t_id}: FAIL")
        else:
            report["checks_passed"].append(f"trigger_present_{t_id}")

    # 5. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Topological alignment proves the framework is 'real'." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_reality_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_reality_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_reconstruction_drift()
    print(json.dumps(res, indent=2))
