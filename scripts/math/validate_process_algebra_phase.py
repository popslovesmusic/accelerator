import json
import os
from datetime import datetime

def validate_process_algebra_phase():
    registry_path = "registry/math/process_algebra_phase_registry.json"
    doc_path = "docs/math/process_algebra_phase_declaration.md"
    result_path = "validation/results/process_algebra_phase_result.json"
    
    report = {
        "validation_id": "VAL-PALG-PHASE-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("process algebra phase registry missing")
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        
    # 1. Governance Invariant Check
    constraints = registry.get("governance_constraints", {})
    if constraints.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden theorem status escalation in phase registry")
        
    if constraints.get("scope_status") != "STRICTLY_LOCAL_RESTRICTED_DOMAIN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden scope status escalation in phase registry")

    # 2. Forbidden Escalation Completeness
    forbidden = constraints.get("forbidden_escalations", [])
    required_forbidden = [
        "do_not_claim_QM_GR_unification",
        "do_not_claim_new_arithmetic_replaces_standard_arithmetic"
    ]
    for req in required_forbidden:
        if req not in forbidden:
            report["status"] = "fail"
            report["governance_violations"].append(f"missing mandatory forbidden escalation rule: {req}")

    # 3. Documentation Alignment
    if os.path.exists(doc_path):
        with open(doc_path, 'r') as f:
            content = f.read()
            if "NOT_PROVEN" not in content or "STRICTLY_LOCAL" not in content:
                report["status"] = "fail"
                report["governance_violations"].append("mandatory status labels missing from documentation")
    else:
        report["status"] = "warning"
        report["governance_violations"].append("phase documentation missing")

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_process_algebra_phase()
    print(json.dumps(res, indent=2))
