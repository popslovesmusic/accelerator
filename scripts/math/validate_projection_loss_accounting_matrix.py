import json
import os
from datetime import datetime

def validate_projection_loss_accounting_matrix():
    registry_path = "registry/math/projection_loss_accounting_matrix.json"
    result_path = "validation/results/projection_loss_accounting_matrix_result.json"
    
    report = {
        "validation_id": "VAL-PLAM-VALID-001",
        "status": "pass",
        "projections_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("matrix registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Matrix Status Check
    if registry.get("matrix_status") != "CANDIDATE_LOSS_ACCOUNTING_MATRIX":
        report["status"] = "fail"
        report["governance_violations"].append("illegal matrix status in registry")
    
    # 2. Source Relation Verification
    source = registry.get("source_relation", {})
    if source.get("symbol") != "⇔R":
        report["status"] = "fail"
        report["governance_violations"].append("source relation symbol mismatch")
    if source.get("canonical_interpretation") != "simultaneous_recursive_aspect_binding":
        report["status"] = "fail"
        report["governance_violations"].append("canonical interpretation mismatch")

    # 3. Matrix Completeness Check
    matrix = registry.get("projection_matrix", [])
    required_projections = ["equality", "implication", "composition", "logical_biconditional"]
    registered_projections = [p["projection"] for p in matrix]
    for rp in required_projections:
        if rp not in registered_projections:
            report["status"] = "fail"
            report["governance_violations"].append(f"required projection missing from matrix: {rp}")
        else:
            report["projections_verified"] += 1
            
    for entry in matrix:
        if not entry.get("retained_features") or not entry.get("lost_or_abstracted_features") or not entry.get("primary_risk"):
            report["status"] = "fail"
            report["governance_violations"].append(f"incomplete data for projection: {entry.get('projection')}")

    # 4. Critical Loss Categorization Check
    critical = registry.get("loss_categories", {}).get("critical_loss", [])
    required_critical = ["residue_history", "recursive_co_generation", "whole_relation_indivisibility"]
    for rc in required_critical:
        if rc not in critical:
            report["status"] = "fail"
            report["governance_violations"].append(f"missing critical loss category: {rc}")

    # 5. Forbidden Interpretations Check
    forbidden = registry.get("forbidden_interpretations", [])
    if not any("replace the source relation" in u for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden replacement check")

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
    res = validate_projection_loss_accounting_matrix()
    print(json.dumps(res, indent=2))
