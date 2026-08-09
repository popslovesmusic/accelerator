import json
import os
from datetime import datetime

def validate_recursive_polarity_preservation_law():
    registry_path = "registry/math/recursive_polarity_preservation_law_registry.json"
    result_path = "validation/results/recursive_polarity_preservation_law_result.json"
    
    report = {
        "validation_id": "VAL-LAW-RPP-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("law registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Core Identification
    if registry.get("symbolic_form") != "(-1) ⇔R (+1)":
        report["status"] = "fail"
        report["governance_violations"].append("symbolic form mismatch")

    if registry.get("status") != "CANDIDATE_LAW":
        report["status"] = "fail"
        report["governance_violations"].append("illegal final law status")

    # 2. Rule Presence
    formal = registry.get("formal_seed", {})
    required_rules = ["process_unit", "non_isolation_rule", "non_arithmetic_rule"]
    for rule in required_rules:
        if rule not in formal:
            report["status"] = "fail"
            report["governance_violations"].append(f"missing formal rule: {rule}")
            
    if "ΩR" not in formal.get("process_unit", ""):
         report["status"] = "fail"
         report["governance_violations"].append("missing ΩR unit definition")

    # 3. Forbidden Claims
    forbidden = registry.get("forbidden_uses", [])
    if not any("standard arithmetic" in u or "-1 equals +1" in u for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden standard arithmetic claim check")
    if not any("magnetism" in u or "monopole" in u for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden physical magnetism claim check")

    # 4. Governance Status
    gov = registry.get("governance_status", {})
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append("physics status must be NON_PHYSICAL_ANALOG_MODEL")
    if gov.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden theorem status escalation")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_recursive_polarity_preservation_law()
    print(json.dumps(res, indent=2))
