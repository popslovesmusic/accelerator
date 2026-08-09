import json
import os
from datetime import datetime

def validate_bridge_metrics_phase():
    registry_path = "registry/math/bridge_metrics_phase_declaration.json"
    result_path = "validation/results/bridge_metrics_phase_result.json"
    
    report = {
        "validation_id": "VAL-BMP-VALID-001",
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
    
    # 2. series_status_equals_METRICS_SCAFFOLD_ONLY
    if gov.get("series_status") != "METRICS_SCAFFOLD_ONLY":
        report["status"] = "fail"
        report["governance_violations"].append(f"series_status_equals_METRICS_SCAFFOLD_ONLY: FAIL (found {gov.get('series_status')})")
    else:
        report["checks_passed"].append("series_status_equals_METRICS_SCAFFOLD_ONLY")

    # 3. phase_definition_present
    if "phase_definition" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("phase_definition_present: FAIL")
    else:
        report["checks_passed"].append("phase_definition_present")

    # 4. metrics_scope_present
    if "metrics_scope" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("metrics_scope_present: FAIL")
    else:
        report["checks_passed"].append("metrics_scope_present")

    # 5. governance_rules_present
    if "governance_rules" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("governance_rules_present: FAIL")
    else:
        report["checks_passed"].append("governance_rules_present")

    # 6. required_metadata_present
    if "required_metadata" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("required_metadata_present: FAIL")
    else:
        report["checks_passed"].append("required_metadata_present")

    # 7-9. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    required_forbidden = [
        ("High trace quality proves physical reality.", "forbidden_claims_include_trace_quality_proves_reality"),
        ("Coherence scores derive physical constants.", "forbidden_claims_include_coherence_derives_constants"),
        ("Safety index replaces governance review.", "forbidden_claims_include_safety_index_replaces_review")
    ]
    for claim, check_name in required_forbidden:
        if claim not in forbidden:
            report["status"] = "fail"
            report["governance_violations"].append(f"{check_name}: FAIL (missing '{claim}')")
        else:
            report["checks_passed"].append(check_name)

    # 11. physics_status_equals_NON_PHYSICAL_ANALOG_MODEL
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append(f"physics_status_equals_NON_PHYSICAL_ANALOG_MODEL: FAIL (found {gov.get('physics_status')})")
    else:
        report["checks_passed"].append("physics_status_equals_NON_PHYSICAL_ANALOG_MODEL")

    # 12. theorem_status_equals_NOT_PROVEN
    if gov.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append(f"theorem_status_equals_NOT_PROVEN: FAIL (found {gov.get('theorem_status')})")
    else:
        report["checks_passed"].append("theorem_status_equals_NOT_PROVEN")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_bridge_metrics_phase()
    print(json.dumps(res, indent=2))
