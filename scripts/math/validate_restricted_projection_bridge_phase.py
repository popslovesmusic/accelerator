import json
import os
from datetime import datetime

def validate_restricted_projection_bridge_phase():
    registry_path = "registry/math/restricted_projection_bridge_phase_declaration.json"
    result_path = "validation/results/restricted_projection_bridge_phase_result.json"
    
    report = {
        "validation_id": "VAL-RPBP-VALID-001",
        "status": "pass",
        "constraints_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("bridge phase registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Bridge Status Check
    if registry.get("bridge_status") != "SCAFFOLD_ONLY":
        report["status"] = "fail"
        report["governance_violations"].append("illegal bridge status: must be SCAFFOLD_ONLY")
    
    # 2. Hard Constraints Check
    constraints = registry.get("hard_constraints", [])
    required_constraints = ["No QM/GR unification claim.", "No physical law claim."]
    for rc in required_constraints:
        if rc not in constraints:
            report["status"] = "fail"
            report["governance_violations"].append(f"missing mandatory hard constraint: {rc}")
        else:
            report["constraints_verified"] += 1

    # 3. Forbidden Claims Check
    forbidden = registry.get("forbidden_claims", [])
    if not any("Unification" in u for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden unification claim check")

    # 4. Governance Status Invariants
    gov = registry.get("governance_status", {})
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append("physics status must be NON_PHYSICAL_ANALOG_MODEL")
    if gov.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden theorem status escalation")
    if gov.get("bridge_status") != "SCAFFOLD_ONLY":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden bridge status escalation")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_restricted_projection_bridge_phase()
    print(json.dumps(res, indent=2))
