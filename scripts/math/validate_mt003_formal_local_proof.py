import json
import os
from datetime import datetime

def validate_mt003_formal_local_proof():
    registry_path = "registry/math/mt003_formal_local_proof_review.json"
    result_path = "validation/results/mt003_formal_local_proof_result.json"
    
    report = {
        "validation_id": "VAL-MT003-FPR-VALID-001",
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

    # 3. tracks_fields_present
    findings = registry.get("review_findings", {})
    tracks = findings.get("track_fields", {})
    required_tracks = ["delta_selection_semantics", "non-null_mismatch_assumptions", "admissible_image_construction", "empty-image_boundary_conditions"]
    for track in required_tracks:
        if track not in tracks:
            report["status"] = "fail"
            report["governance_violations"].append(f"track_missing_{track}: FAIL")
        else:
            report["checks_passed"].append(f"track_present_{track}")

    # 4. result_allowed
    allowed_results = ["LOCALLY_DERIVABLE_UNDER_ASSUMPTIONS", "ASSUMPTION_INSUFFICIENT", "COUNTEREXAMPLE_FOUND", "PROOF_BLOCKED"]
    if findings.get("proof_result") not in allowed_results:
        report["status"] = "fail"
        report["governance_violations"].append(f"invalid_proof_result: FAIL (found {findings.get('proof_result')})")
    else:
        report["checks_passed"].append("valid_proof_result")

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
    res = validate_mt003_formal_local_proof()
    print(json.dumps(res, indent=2))
