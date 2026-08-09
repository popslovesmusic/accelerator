import json
import os
from datetime import datetime

def validate_participatory_refinement_phase():
    registry_path = "registry/math/participatory_refinement_phase_declaration.json"
    result_path = "validation/results/participatory_refinement_phase_result.json"
    
    report = {
        "validation_id": "VAL-PAR-PHASE-VALID-001",
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
    
    # 2. series_status_equals_POST_PFS_REFINEMENT_PHASE
    if gov.get("series_status") != "POST_PFS_REFINEMENT_PHASE":
        report["status"] = "fail"
        report["governance_violations"].append(f"series_status_equals_POST_PFS_REFINEMENT_PHASE: FAIL (found {gov.get('series_status')})")
    else:
        report["checks_passed"].append("series_status_equals_POST_PFS_REFINEMENT_PHASE")

    # 3. core_principle_present
    if "phase_definition" not in registry or "core_principle" not in registry["phase_definition"]:
        report["status"] = "fail"
        report["governance_violations"].append("core_principle_present: FAIL")
    else:
        report["checks_passed"].append("core_principle_present")

    # 4. governance_rules_present
    if "governance_rules" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("governance_rules_present: FAIL")
    else:
        report["checks_passed"].append("governance_rules_present")

    # 5. hardening_boilerplate_present
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

    # 6. non_claims checks
    non_claims = registry.get("non_claims", [])
    required_non_claims = [
        ("Simplicity implies physical truth.", "non_claims_include_simplicity_no_truth"),
        ("Operator reduction derives universal unification.", "non_claims_include_no_unification")
    ]
    for claim, check_name in required_non_claims:
        if claim not in non_claims:
            report["status"] = "fail"
            report["governance_violations"].append(f"{check_name}: FAIL (missing '{claim}')")
        else:
            report["checks_passed"].append(check_name)

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_participatory_refinement_phase()
    print(json.dumps(res, indent=2))
