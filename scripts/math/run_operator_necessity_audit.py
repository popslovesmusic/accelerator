import json
import os
from datetime import datetime

def run_operator_necessity_audit():
    registry_path = "registry/math/operator_necessity_audit.json"
    result_path = "validation/results/operator_necessity_audit_result.json"
    
    report = {
        "validation_id": "VAL-ONA-RUN-001",
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

    # 3. irreducible_operators_present
    ops = registry.get("retained_operators", [])
    required_symbols = ["Pi_A", "NavT", "delta", "Transition_Operator", "R", "CSI", "-(i)", "<->_R"]
    found_symbols = [o.get("symbol") for o in ops]
    for sym in required_symbols:
        if sym not in found_symbols:
            report["status"] = "fail"
            report["governance_violations"].append(f"irreducible_operator_missing_{sym}: FAIL")
        else:
            report["checks_passed"].append(f"irreducible_operator_present_{sym}")

    # 4. all_operators_irreducible
    all_irreducible = all(o.get("status") == "IRREDUCIBLE" for o in ops)
    if not all_irreducible:
        report["status"] = "fail"
        report["governance_violations"].append("operator_status_check: FAIL (some operators not marked IRREDUCIBLE)")
    else:
        report["checks_passed"].append("operator_status_check_pass")

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
    res = run_operator_necessity_audit()
    print(json.dumps(res, indent=2))
