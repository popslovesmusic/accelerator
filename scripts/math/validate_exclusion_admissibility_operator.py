import json
import os
from datetime import datetime

def validate_exclusion_admissibility_operator():
    registry_path = "registry/math/exclusion_admissibility_operator_registry.json"
    result_path = "validation/results/exclusion_admissibility_operator_result.json"
    
    report = {
        "validation_id": "VAL-OP-EAA-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("operator registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Core Identification
    if registry.get("symbol") != "ΠE":
        report["status"] = "fail"
        report["governance_violations"].append(f"operator symbol mismatch: expected ΠE, got {registry.get('symbol')}")

    if registry.get("associated_expression") != "(E≠0)":
        report["status"] = "fail"
        report["governance_violations"].append(f"associated expression mismatch: expected (E≠0), got {registry.get('associated_expression')}")

    if registry.get("status") != "CANDIDATE_OPERATOR":
        report["status"] = "fail"
        report["governance_violations"].append("illegal final operator status")

    # 2. Rule Presence
    formal = registry.get("formal_seed", {})
    required_rules = ["null_rule", "non_arithmetic_rule", "idempotence_candidate"]
    for rule in required_rules:
        if rule not in formal:
            report["status"] = "fail"
            report["governance_violations"].append(f"missing formal rule: {rule}")

    # 3. Forbidden Claims
    forbidden = registry.get("forbidden_uses", [])
    if not any("physical_energy_claim" in u or "conserved physical energy" in u for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden physical energy claim check")

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
    res = validate_exclusion_admissibility_operator()
    print(json.dumps(res, indent=2))
