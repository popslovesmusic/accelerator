import json
import os
from datetime import datetime

def validate_mt_proof_obligations():
    registry_path = "registry/math/mt_proof_obligation_registry.json"
    result_path = "validation/results/mt_proof_obligation_result.json"
    
    report = {
        "validation_id": "VAL-OB-VALID-001",
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

    # 3. obligations_present
    obs = registry.get("proof_obligations", [])
    required_ids = ["MT-001", "MT-002", "MT-003"]
    found_ids = [o.get("theorem_id") for o in obs]
    for t_id in required_ids:
        if t_id not in found_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"obligation_present_{t_id}: FAIL")
        else:
            report["checks_passed"].append(f"obligation_present_{t_id}")

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
    res = validate_mt_proof_obligations()
    print(json.dumps(res, indent=2))
