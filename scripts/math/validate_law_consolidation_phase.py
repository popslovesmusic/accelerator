import json
import os
from datetime import datetime

def validate_law_consolidation_phase():
    registry_path = "registry/math/law_consolidation_phase_declaration.json"
    result_path = "validation/results/law_consolidation_phase_result.json"
    
    report = {
        "validation_id": "VAL-LCP-VALID-001",
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
    
    # 2. series_status_equals_LAW_CONSOLIDATION_ONLY
    if gov.get("series_status") != "LAW_CONSOLIDATION_ONLY":
        report["status"] = "fail"
        report["governance_violations"].append(f"series_status_equals_LAW_CONSOLIDATION_ONLY: FAIL (found {gov.get('series_status')})")
    else:
        report["checks_passed"].append("series_status_equals_LAW_CONSOLIDATION_ONLY")

    # 3. phase_definition_present
    if "phase_definition" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("phase_definition_present: FAIL")
    else:
        report["checks_passed"].append("phase_definition_present")
        if "core_principle" not in registry["phase_definition"]:
            report["status"] = "fail"
            report["governance_violations"].append("core_principle_missing: FAIL")
        else:
            report["checks_passed"].append("core_principle_present")

    # 4. governance_rules_present
    if "governance_rules" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("governance_rules_present: FAIL")
    else:
        report["checks_passed"].append("governance_rules_present")

    # 5. required_metadata_present
    if "required_metadata" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("required_metadata_present: FAIL")
    else:
        report["checks_passed"].append("required_metadata_present")

    # 6. hardening_boilerplate_present
    if registry.get("source_relation") != "(E≠0) ⇔R δ(E>0)":
        report["status"] = "fail"
        report["governance_violations"].append("hardening_boilerplate_source_relation: FAIL")
    else:
        report["checks_passed"].append("hardening_boilerplate_source_relation")
        
    if registry.get("non_separability_acknowledged") is not True:
        report["status"] = "fail"
        report["governance_violations"].append("hardening_boilerplate_non_separability: FAIL")
    else:
        report["checks_passed"].append("hardening_boilerplate_non_separability")

    # 7-9. non_claims checks
    non_claims = registry.get("non_claims", [])
    required_non_claims = [
        ("Deleting prior laws is permitted.", "non_claims_include_non_deletion"),
        ("Consolidation proves theorem validity.", "non_claims_include_no_theorem_promotion")
    ]
    for claim, check_name in required_non_claims:
        if claim not in non_claims:
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

    # 12. theorem_status_equals_NO_THEOREM_PROMOTION
    if gov.get("theorem_status") != "NO_THEOREM_PROMOTION":
        report["status"] = "fail"
        report["governance_violations"].append(f"theorem_status_equals_NO_THEOREM_PROMOTION: FAIL (found {gov.get('theorem_status')})")
    else:
        report["checks_passed"].append("theorem_status_equals_NO_THEOREM_PROMOTION")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_law_consolidation_phase()
    print(json.dumps(res, indent=2))
