import json
import os
from datetime import datetime

def validate_mt_counterexample_boundary_map():
    registry_path = "registry/math/mt_counterexample_boundary_map.json"
    result_path = "validation/results/mt_counterexample_boundary_map_result.json"
    
    report = {
        "validation_id": "VAL-CE-VALID-001",
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

    # 3. failures_present
    ce_map = registry.get("counterexample_map", [])
    required_ids = ["projection_non_idempotence", "transport_identity_failure", "empty_admissible_image", "recursive_divergence"]
    found_ids = [c.get("failure_id") for c in ce_map]
    for f_id in required_ids:
        if f_id not in found_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"failure_present_{f_id}: FAIL")
        else:
            report["checks_passed"].append(f"failure_present_{f_id}")

    # 4. mandatory_rules_present
    rules = registry.get("governance_rules", [])
    if len(rules) < 2:
        report["status"] = "fail"
        report["governance_violations"].append("mandatory_rules_present: FAIL (insufficient count)")
    else:
        report["checks_passed"].append("mandatory_rules_present")

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
    res = validate_mt_counterexample_boundary_map()
    print(json.dumps(res, indent=2))
