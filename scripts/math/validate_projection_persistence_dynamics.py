import json
import os
from datetime import datetime

def validate_projection_persistence_dynamics():
    registry_path = "registry/math/projection_persistence_dynamics.json"
    result_path = "validation/results/projection_persistence_dynamics_result.json"
    
    report = {
        "validation_id": "VAL-PPD-VALID-001",
        "status": "pass",
        "states_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("projection persistence dynamics registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Framework Identification
    if registry.get("dynamics_status") != "CANDIDATE_PERSISTENCE_DYNAMICS":
        report["status"] = "fail"
        report["governance_violations"].append("illegal dynamics status in registry")

    # 2. State Completeness Check
    states = registry.get("dynamic_states", [])
    required_states = ["PPD-1", "PPD-2", "PPD-3", "PPD-4", "PPD-5"]
    registered_ids = [s["state_id"] for s in states]
    for rs in required_states:
        if rs not in registered_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"required dynamic state missing: {rs}")
        else:
            report["states_verified"] += 1

    # 3. Core Definition and Rules Check
    definition = registry.get("core_definition", {})
    if not definition.get("canonical_statement") or not definition.get("non_primitive_rule"):
        report["status"] = "fail"
        report["governance_violations"].append("missing core definition or non-primitive rule")

    if not registry.get("transition_conditions"):
        report["status"] = "fail"
        report["governance_violations"].append("missing transition conditions in registry")

    if not registry.get("governance_rules"):
        report["status"] = "fail"
        report["governance_violations"].append("missing governance rules in registry")

    # 4. Forbidden Uses Check
    forbidden = registry.get("forbidden_uses", [])
    if not any("physical spacetime evolution" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden physical spacetime evolution check")
    if not any("qm/gr" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden qm/gr evidence check")

    # 5. Governance Status Invariants
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
    res = validate_projection_persistence_dynamics()
    print(json.dumps(res, indent=2))
