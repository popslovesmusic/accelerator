import json
import os
from datetime import datetime

def validate_minimal_expression_set():
    registry_path = "registry/math/process_algebra_minimal_expression_set.json"
    result_path = "validation/results/process_algebra_minimal_expression_set_result.json"
    
    report = {
        "validation_id": "VAL-PALG-EXPR-VALID-001",
        "status": "pass",
        "approved_forms_verified": 0,
        "banned_forms_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("minimal expression set registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Registry Status Check
    if registry.get("registry_status") != "CANDIDATE_EXPRESSION_SET":
        report["status"] = "fail"
        report["governance_violations"].append("illegal registry status")

    # 2. Approved Forms Check
    approved = registry.get("approved_expression_forms", [])
    required_ids = [
        "PALG-EXPR-001", "PALG-EXPR-002", "PALG-EXPR-003", "PALG-EXPR-004"
    ]
    for r_id in required_ids:
        if not any(e["expression_id"] == r_id for e in approved):
            report["status"] = "fail"
            report["governance_violations"].append(f"required approved expression missing: {r_id}")
        else:
            report["approved_forms_verified"] += 1

    # 3. Banned Forms Check
    banned = registry.get("banned_expression_forms", [])
    required_banned = ["-1 = +1", "QM = GR"]
    for b_form in required_banned:
        if not any(b_form in e["form"] for e in banned):
            report["status"] = "fail"
            report["governance_violations"].append(f"required banned form missing: {b_form}")
        else:
            report["banned_forms_verified"] += 1

    # 4. Restricted Forms Constraints
    restricted = registry.get("restricted_expression_forms", [])
    for r in restricted:
        if not r.get("condition"):
            report["status"] = "fail"
            report["governance_violations"].append(f"restricted form {r['form']} missing condition")

    # 5. Governance Status
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
    res = validate_minimal_expression_set()
    print(json.dumps(res, indent=2))
