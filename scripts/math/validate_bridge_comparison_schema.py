import json
import os
from datetime import datetime

def validate_bridge_comparison_schema():
    registry_path = "registry/math/bridge_comparison_schema.json"
    result_path = "validation/results/bridge_comparison_schema_result.json"
    
    report = {
        "validation_id": "VAL-BCS-VALID-001",
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
    
    # 2. bridge_status_equals_COMPARISON_ONLY
    if status.get("bridge_status") != "COMPARISON_ONLY":
        report["status"] = "fail"
        report["governance_violations"].append(f"bridge_status_equals_COMPARISON_ONLY: FAIL (found {status.get('bridge_status')})")
    else:
        report["checks_passed"].append("bridge_status_equals_COMPARISON_ONLY")

    # 3. comparison_dimensions_include_BCD001_to_BCD006
    dimensions = registry.get("comparison_dimensions", [])
    dim_ids = [d.get("dimension_id") for d in dimensions]
    required_dims = [f"BCD-{str(i).zfill(3)}" for i in range(1, 7)]
    missing_dims = [rd for rd in required_dims if rd not in dim_ids]
    if missing_dims:
        report["status"] = "fail"
        report["governance_violations"].append(f"comparison_dimensions_include_BCD001_to_BCD006: FAIL (missing {missing_dims})")
    else:
        report["checks_passed"].append("comparison_dimensions_include_BCD001_to_BCD006")

    # 4. comparison_record_schema_present
    if "comparison_record_schema" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("comparison_record_schema_present: FAIL")
    else:
        report["checks_passed"].append("comparison_record_schema_present")

    # 5. example_records_present
    if "example_records" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("example_records_present: FAIL")
    else:
        report["checks_passed"].append("example_records_present")

    # 6. governance_rules_present
    if "governance_rules" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("governance_rules_present: FAIL")
    else:
        report["checks_passed"].append("governance_rules_present")

    # 7-8. forbidden_uses checks
    forbidden = registry.get("forbidden_uses", [])
    required_forbidden = [
        ("Claiming QM-like and GR-like projections are unified.", "forbidden_uses_include_QM_GR_unified"),
        ("Claiming projection coherence proves physical reality.", "forbidden_uses_include_projection_coherence_proves_reality")
    ]
    for use, check_name in required_forbidden:
        if use not in forbidden:
            report["status"] = "fail"
            report["governance_violations"].append(f"{check_name}: FAIL (missing '{use}')")
        else:
            report["checks_passed"].append(check_name)

    # 9. physics_status_equals_NON_PHYSICAL_ANALOG_MODEL
    if status.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append(f"physics_status_equals_NON_PHYSICAL_ANALOG_MODEL: FAIL (found {status.get('physics_status')})")
    else:
        report["checks_passed"].append("physics_status_equals_NON_PHYSICAL_ANALOG_MODEL")

    # 10. theorem_status_equals_NOT_PROVEN
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
    res = validate_bridge_comparison_schema()
    print(json.dumps(res, indent=2))
