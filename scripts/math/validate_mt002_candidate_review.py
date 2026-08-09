import json
import os
from datetime import datetime

def validate_mt002_candidate_review():
    registry_path = "registry/math/mt002_transport_identity_candidate_review.json"
    result_path = "validation/results/mt002_candidate_review_result.json"
    
    report = {
        "validation_id": "VAL-MT002-REV-VALID-001",
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

    # 3. must_address_coverage_present
    findings = registry.get("review_findings", {})
    coverage = findings.get("must_address_coverage", [])
    required_address = ["orientation_space_clarity", "identity_transport_condition", "transport_equivalence_definition"]
    for item in required_address:
        if item not in coverage:
            report["status"] = "fail"
            report["governance_violations"].append(f"coverage_missing_{item}: FAIL")
        else:
            report["checks_passed"].append(f"coverage_present_{item}")

    # 4. status_allowed
    allowed_results = ["CANDIDATE_SUPPORTED_UNDER_ASSUMPTIONS", "REQUIRES_ADDITIONAL_PRECONDITIONS", "COUNTEREXAMPLE_FOUND", "REVIEW_BLOCKED"]
    if findings.get("candidate_derivation") not in allowed_results:
        report["status"] = "fail"
        report["governance_violations"].append(f"invalid_candidate_status: FAIL (found {findings.get('candidate_derivation')})")
    else:
        report["checks_passed"].append("valid_candidate_status")

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
    res = validate_mt002_candidate_review()
    print(json.dumps(res, indent=2))
