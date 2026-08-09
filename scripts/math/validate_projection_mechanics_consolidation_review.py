import json
import os
from datetime import datetime

def validate_projection_mechanics_consolidation_review():
    registry_path = "registry/math/projection_mechanics_consolidation_review.json"
    result_path = "validation/results/projection_mechanics_consolidation_review_result.json"
    
    report = {
        "validation_id": "VAL-PMCR-VALID-001",
        "status": "pass",
        "findings_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("consolidation review registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Review Status Check
    if registry.get("review_status") != "CONSOLIDATION_REVIEW_ONLY":
        report["status"] = "fail"
        report["governance_violations"].append("illegal review status in registry")

    # 2. Scope and Finding Completeness Check
    if not registry.get("review_scope") or not registry.get("review_findings"):
        report["status"] = "fail"
        report["governance_violations"].append("missing review scope or findings")
    else:
        report["findings_verified"] = len(registry.get("review_findings", []))

    # 3. Risk and Rules Presence
    if not registry.get("remaining_risks") or not registry.get("consolidated_governance_rules"):
        report["status"] = "fail"
        report["governance_violations"].append("missing risk documentation or consolidated rules")

    # 4. Result Invariants
    result = registry.get("review_result", {})
    if result.get("projection_mechanics_layer_status") != "STABILIZED_CANDIDATE_FRAMEWORK":
        report["status"] = "fail"
        report["governance_violations"].append("incorrect layer status")
    
    if result.get("physics_bridge_status") != "NOT_APPROVED":
        report["status"] = "fail"
        report["governance_violations"].append("physics bridge must remain NOT_APPROVED in this review")

    # 5. Forbidden Next Steps Check
    forbidden = registry.get("forbidden_next_steps", [])
    if not any("QM/GR unification" in u for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden QM/GR unification check")

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
    res = validate_projection_mechanics_consolidation_review()
    print(json.dumps(res, indent=2))
