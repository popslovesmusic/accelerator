import json
import os
from datetime import datetime

def validate_nested_relation_semantics_governance():
    registry_path = "registry/math/nested_relation_semantics_governance.json"
    result_path = "validation/results/nested_relation_semantics_governance_result.json"
    
    report = {
        "validation_id": "VAL-NRSG-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("semantics registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Semantics Status Check
    if registry.get("semantics_status") != "CANDIDATE_GOVERNANCE":
        report["status"] = "fail"
        report["governance_violations"].append("illegal semantics status in registry")
    
    # 2. Core Definition Check
    core = registry.get("core_definition", {})
    if core.get("primitive_interpretation") != "simultaneous_recursive_aspect_binding":
        report["status"] = "fail"
        report["governance_violations"].append("missing or incorrect core primitive interpretation")

    # 3. Rule Presence Check
    constraints = registry.get("semantic_constraints", {})
    required_rules = [
        "simultaneity_rule", "anti_flattening_rule", 
        "non_associativity_rule", "non_transitivity_rule", 
        "projection_exception_rule"
    ]
    for rule in required_rules:
        if rule not in constraints:
            report["status"] = "fail"
            report["governance_violations"].append(f"missing mandatory semantic rule: {rule}")

    # 4. Projection Reduction Targets Check
    targets = [t["target"] for t in registry.get("projection_reduction_targets", [])]
    required_targets = ["equality", "implication", "composition", "logical_biconditional"]
    for t in required_targets:
        if t not in targets:
            report["status"] = "fail"
            report["governance_violations"].append(f"required projection reduction target missing: {t}")

    # 5. Forbidden Uses Check
    forbidden = registry.get("forbidden_uses", [])
    if "sequential_execution" not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden sequential execution check")

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
    res = validate_nested_relation_semantics_governance()
    print(json.dumps(res, indent=2))
