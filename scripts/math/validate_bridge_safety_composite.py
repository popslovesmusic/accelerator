import json
import os
from datetime import datetime

def validate_bridge_safety_composite():
    registry_path = "registry/math/bridge_safety_composite_index.json"
    result_path = "validation/results/bridge_safety_composite_result.json"
    
    report = {
        "validation_id": "VAL-BSCI-VALID-001",
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

    # 3. composite_schema_present
    if "composite_schema" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("composite_schema_present: FAIL")
    else:
        report["checks_passed"].append("composite_schema_present")

    # 4. critical_overrides_present
    if "critical_overrides" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("critical_overrides_present: FAIL")
    else:
        report["checks_passed"].append("critical_overrides_present")

    # 5. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Safety index score proves physical validity." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_safety_validity_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_safety_validity_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_bridge_safety_composite()
    print(json.dumps(res, indent=2))
