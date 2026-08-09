import json
import os
from datetime import datetime

def validate_counterexample_disclosure():
    registry_path = "registry/math/counterexample_disclosure_registry.json"
    result_path = "validation/results/counterexample_disclosure_result.json"
    
    report = {
        "validation_id": "VAL-DIS-VALID-001",
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

    # 3. disclosures_present
    disclosures = registry.get("disclosures", [])
    required_ids = ["recursive_divergence", "branch_explosion", "orientation_locking", "projection_loss", "fragmentation", "indistinguishable_collapse"]
    found_ids = [d.get("disclosure_id") for d in disclosures]
    for d_id in required_ids:
        if d_id not in found_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"disclosure_present_{d_id}: FAIL")
        else:
            report["checks_passed"].append(f"disclosure_present_{d_id}")

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
    res = validate_counterexample_disclosure()
    print(json.dumps(res, indent=2))
