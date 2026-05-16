import json
import os
from datetime import datetime

def validate_nested_whole_relation_review():
    registry_path = "registry/math/nested_whole_relation_candidate_review.json"
    result_path = "validation/results/nested_whole_relation_candidate_review_result.json"
    
    report = {
        "validation_id": "VAL-PALG-NWR-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("review registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Review Target Verification
    target = registry.get("review_target", {})
    if not target:
        report["status"] = "fail"
        report["governance_violations"].append("missing review target")
    
    # 2. Required Findings and Risks
    findings = registry.get("review_findings", {})
    if not findings.get("supported_interpretations"):
        report["status"] = "fail"
        report["governance_violations"].append("missing supported interpretations")
    if not findings.get("unresolved_risks"):
        report["status"] = "fail"
        report["governance_violations"].append("missing unresolved risks")

    # 3. Constraint Presence
    constraints = registry.get("provisional_constraints", {})
    required_rules = [
        "simultaneity_rule", "non_associativity_rule", "non_transitivity_rule"
    ]
    for rule in required_rules:
        if rule not in constraints:
            report["status"] = "fail"
            report["governance_violations"].append(f"missing mandatory constraint: {rule}")

    # 4. Forbidden Readings
    if not registry.get("forbidden_readings"):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden readings")

    # 5. Final Result Status Check
    res = registry.get("review_result", {})
    if res.get("overall_status") != "PASS_WITH_WARNINGS":
        report["status"] = "fail"
        report["governance_violations"].append("overall_status mismatch")
    
    if res.get("promotion_status") != "NOT_APPROVED_FOR_PRIMITIVE_PROMOTION":
        report["status"] = "fail"
        report["governance_violations"].append("illegal promotion status in review")

    # 6. Governance Status
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
    res = validate_nested_whole_relation_review()
    print(json.dumps(res, indent=2))
