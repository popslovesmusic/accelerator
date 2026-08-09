import json
import os
from datetime import datetime

def validate_operator_signature_hardening():
    registry_path = "registry/math/operator_signature_hardening_registry.json"
    result_path = "validation/results/operator_signature_hardening_result.json"
    
    report = {
        "validation_id": "VAL-OSH-VALID-001",
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

    # 3. operators_present
    ops = registry.get("operators", [])
    required_symbols = ["Pi_A", "NavT", "delta", "CSI", "minus_i"]
    found_symbols = [o.get("symbol") for o in ops]
    for sym in required_symbols:
        if sym not in found_symbols:
            report["status"] = "fail"
            report["governance_violations"].append(f"operator_present_{sym}: FAIL")
        else:
            report["checks_passed"].append(f"operator_present_{sym}")

    # 4. operator_fields_check
    for o in ops:
        sym = o.get("symbol")
        required_fields = ["domain", "codomain", "input_types", "output_types", "preconditions", "postconditions", "failure_modes"]
        for field in required_fields:
            if field not in o:
                report["status"] = "fail"
                report["governance_violations"].append(f"operator_field_missing_{sym}_{field}: FAIL")
            else:
                report["checks_passed"].append(f"operator_field_present_{sym}_{field}")

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
    res = validate_operator_signature_hardening()
    print(json.dumps(res, indent=2))
