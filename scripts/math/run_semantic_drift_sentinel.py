import json
import os
from datetime import datetime

def run_semantic_drift_sentinel():
    registry_path = "registry/math/semantic_drift_sentinel.json"
    result_path = "validation/results/semantic_drift_sentinel_result.json"
    
    report = {
        "validation_id": "VAL-SDS-RUN-001",
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

    # 3. sentinel_patterns_active
    patterns = registry.get("sentinel_patterns", [])
    all_active = all(p.get("status") == "ACTIVE" for p in patterns)
    if not all_active:
        report["status"] = "fail"
        report["governance_violations"].append("sentinel_patterns_activation: FAIL (not all patterns active)")
    else:
        report["checks_passed"].append("sentinel_patterns_activation_pass")

    # 4. pattern_coverage_check
    required_patterns = ["new_alias_growth", "hidden_equivalence_language", "ontology_reification", "globality_injection", "relation_collapse", "objectification_patterns"]
    found_patterns = [p.get("pattern_id") for p in patterns]
    for rp in required_patterns:
        if rp not in found_patterns:
            report["status"] = "fail"
            report["governance_violations"].append(f"sentinel_pattern_missing_{rp}: FAIL")
        else:
            report["checks_passed"].append(f"sentinel_pattern_present_{rp}")

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
    res = run_semantic_drift_sentinel()
    print(json.dumps(res, indent=2))
