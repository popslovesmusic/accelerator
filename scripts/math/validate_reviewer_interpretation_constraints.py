import json
import os
from datetime import datetime

def validate_reviewer_interpretation_constraints():
    registry_path = "registry/math/reviewer_interpretation_constraints.json"
    result_path = "validation/results/reviewer_interpretation_constraints_result.json"
    
    report = {
        "validation_id": "VAL-RIC-REG-VALID-001",
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

    # 3. inadmissible_patterns_check
    patterns = registry.get("inadmissible_patterns", [])
    required_ids = ["physics_derivation_claim", "hidden_globality", "ordinary_equivalence_substitution", "object_ontology_injection", "unification_language", "closure_inflation"]
    found_ids = [p.get("pattern_id") for p in patterns]
    for p_id in required_ids:
        if p_id not in found_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"inadmissible_pattern_missing_{p_id}: FAIL")
        else:
            report["checks_passed"].append(f"inadmissible_pattern_present_{p_id}")

    # 4. hardening_boilerplate_present
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
    res = validate_reviewer_interpretation_constraints()
    print(json.dumps(res, indent=2))
