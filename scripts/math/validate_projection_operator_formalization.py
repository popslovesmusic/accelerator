import json
import os
from datetime import datetime

def validate_projection_operator_formalization():
    registry_path = "registry/math/projection_operator_registry.json"
    result_path = "validation/results/projection_operator_formalization_result.json"
    
    report = {
        "validation_id": "VAL-POF-VALID-001",
        "status": "pass",
        "operators_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("projection operator registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Framework Identification
    if registry.get("operator_status") != "CANDIDATE_PROJECTION_OPERATOR_FRAMEWORK":
        report["status"] = "fail"
        report["governance_violations"].append("illegal framework status")
    
    primitive = registry.get("primitive_definition", {})
    if primitive.get("operator_symbol") != "Πx":
        report["status"] = "fail"
        report["governance_violations"].append("operator symbol mismatch: expected Πx")

    # 2. Registered Operators Verification
    operators = registry.get("registered_projection_operators", [])
    required_operators = ["Π_equal", "Π_imply", "Π_compose", "Π_biconditional"]
    registered_ids = [op["operator_id"] for op in operators]
    for ro in required_operators:
        if ro not in registered_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"required projection operator missing: {ro}")
        else:
            report["operators_verified"] += 1

    # 3. Rule and Constraint Check
    constraints = registry.get("projection_operator_constraints", {})
    if not constraints.get("projection_requires_loss_accounting") or not constraints.get("projection_preserves_traceability"):
        report["status"] = "fail"
        report["governance_violations"].append("missing mandatory projection operator constraints")

    if not registry.get("projection_rules"):
        report["status"] = "fail"
        report["governance_violations"].append("missing projection rules in registry")

    # 4. Forbidden Uses Check (Reversibility)
    forbidden = registry.get("forbidden_uses", [])
    if "reversible_by_default" not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden reversibility check")

    # 5. Schema Check
    if not registry.get("projection_operator_schema"):
        report["status"] = "fail"
        report["governance_violations"].append("missing projection operator schema")

    # 6. Governance Status Invariants
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
    res = validate_projection_operator_formalization()
    print(json.dumps(res, indent=2))
