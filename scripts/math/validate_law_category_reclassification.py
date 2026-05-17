import json
import os
from datetime import datetime

def validate_law_category_reclassification():
    registry_path = "registry/math/law_category_reclassification_registry.json"
    result_path = "validation/results/law_category_reclassification_result.json"
    
    report = {
        "validation_id": "VAL-LCR-VALID-001",
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

    # 3. reclassifications_present
    reclass = registry.get("reclassifications", [])
    if len(reclass) < 34:
        report["status"] = "fail"
        report["governance_violations"].append(f"reclassification_coverage: FAIL (found {len(reclass)} laws, expected 34)")
    else:
        report["checks_passed"].append("reclassification_coverage_complete")

    # 4. category_validity_check
    allowed_categories = ["definition", "operator_constraint", "projection_rule", "failure_rule", "derived_consequence_candidate", "theorem_candidate", "governance_constraint"]
    all_valid = all(r.get("category") in allowed_categories for r in reclass)
    if not all_valid:
        report["status"] = "fail"
        report["governance_violations"].append("category_validity: FAIL (invalid category found)")
    else:
        report["checks_passed"].append("all_categories_valid")

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
    res = validate_law_category_reclassification()
    print(json.dumps(res, indent=2))
