import json
import os
from datetime import datetime

def validate_semantic_drift():
    registry_path = "registry/math/semantic_drift_registry.json"
    result_path = "validation/results/semantic_drift_result.json"
    
    report = {
        "validation_id": "VAL-SD-VALID-001",
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
    required_flags = ["absolute_meaning_drift", "translation_equals_identity_drift", "semantic_closure_drift", "observer_independence_drift", "hidden_unification_semantics", "truth_equivalence_drift"]
    found_flags = [f.get("flag_id") for f in flags]
    for f_id in required_flags:
        if f_id not in found_flags:
            report["status"] = "fail"
            report["governance_violations"].append(f"flag_present_{f_id}: FAIL")
        else:
            report["checks_passed"].append(f"flag_present_{f_id}")

    # 4. automatic_review_triggers_present
    triggers = registry.get("automatic_review_triggers", [])
    required_triggers = ["perfect_translation_claimed", "recursive_reference_equals_completion", "semantic_conflict_removed", "observer_externality_assumed"]
    found_triggers = [t.get("trigger_id") for t in triggers]
    for t_id in required_triggers:
        if t_id not in found_triggers:
            report["status"] = "fail"
            report["governance_violations"].append(f"trigger_present_{t_id}: FAIL")
        else:
            report["checks_passed"].append(f"trigger_present_{t_id}")

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
    res = validate_semantic_drift()
    print(json.dumps(res, indent=2))
