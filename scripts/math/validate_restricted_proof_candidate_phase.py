import json
import os
from datetime import datetime

def validate_restricted_proof_candidate_phase():
    registry_path = "registry/math/restricted_proof_candidate_phase_declaration.json"
    result_path = "validation/results/restricted_proof_candidate_phase_result.json"
    
    report = {
        "validation_id": "VAL-RPC-VALID-001",
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
    
    # 2. series_status_equals_RESTRICTED_LOCAL_THEOREM_REVIEW
    if gov.get("series_status") != "RESTRICTED_LOCAL_THEOREM_REVIEW":
        report["status"] = "fail"
        report["governance_violations"].append(f"series_status_equals_RESTRICTED_LOCAL_THEOREM_REVIEW: FAIL (found {gov.get('series_status')})")
    else:
        report["checks_passed"].append("series_status_equals_RESTRICTED_LOCAL_THEOREM_REVIEW")

    # 3. phase_definition_present
    if "phase_definition" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("phase_definition_present: FAIL")
    else:
        report["checks_passed"].append("phase_definition_present")

    # 4. terminology_freeze_present
    if "terminology_freeze" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("terminology_freeze_present: FAIL")
    else:
        report["checks_passed"].append("terminology_freeze_present")

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

    # 7. hardening_boilerplate_present
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

    # 8. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    required_forbidden = [
        ("A supported candidate is a proven theorem.", "forbidden_claims_include_candidate_as_proven"),
        ("Local derivation readiness implies physical relevance.", "forbidden_claims_include_physical_relevance")
    ]
    for claim, check_name in required_forbidden:
        if claim not in forbidden:
            report["status"] = "fail"
            report["governance_violations"].append(f"{check_name}: FAIL (missing '{claim}')")
        else:
            report["checks_passed"].append(check_name)

    # 10. physics_status_equals_NON_PHYSICAL_ANALOG_MODEL
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append(f"physics_status_equals_NON_PHYSICAL_ANALOG_MODEL: FAIL (found {gov.get('physics_status')})")
    else:
        report["checks_passed"].append("physics_status_equals_NON_PHYSICAL_ANALOG_MODEL")

    # 11. theorem_status_equals_PROOF_CANDIDATE_REVIEW_ONLY
    if gov.get("theorem_status") != "PROOF_CANDIDATE_REVIEW_ONLY":
        report["status"] = "fail"
        report["governance_violations"].append(f"theorem_status_equals_PROOF_CANDIDATE_REVIEW_ONLY: FAIL (found {gov.get('theorem_status')})")
    else:
        report["checks_passed"].append("theorem_status_equals_PROOF_CANDIDATE_REVIEW_ONLY")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_restricted_proof_candidate_phase()
    print(json.dumps(res, indent=2))
