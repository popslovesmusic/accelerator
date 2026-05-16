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
        
    # 1. Phase ID Check
    if registry.get("phase_id") != "PROCESS_ALGEBRA_PHASE_001":
        report["status"] = "fail"
        report["governance_violations"].append("phase_id mismatch")

    # 2. Governance Status Check
    gov = registry.get("governance_status", {})
    if gov.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden theorem status escalation")
        
    if gov.get("scope_status") != "STRICTLY_LOCAL_RESTRICTED_DOMAIN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden scope status escalation")
        
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append("physics status must be NON_PHYSICAL_ANALOG_MODEL")

    # 3. Forbidden Claims Presence
    if not registry.get("forbidden_claims"):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden_claims in registry")

    # 4. Operator Candidates Status Check
    for op in registry.get("operator_candidates", []):
        if op.get("status") not in ["candidate_operator", "candidate_object"]:
            report["status"] = "fail"
            report["governance_violations"].append(f"operator {op.get('symbol')} has illegal final status")

    # 5. Documentation Alignment
    if os.path.exists(doc_path):
        with open(doc_path, 'r') as f:
            content = f.read()
            mandatory_labels = ["NOT_PROVEN", "STRICTLY_LOCAL", "NON_PHYSICAL_ANALOG_MODEL"]
            for label in mandatory_labels:
                if label not in content:
                    report["status"] = "fail"
                    report["governance_violations"].append(f"mandatory status label '{label}' missing from documentation")
    else:
        report["status"] = "warning"
        report["governance_violations"].append("phase documentation missing")

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_process_algebra_phase()
    print(json.dumps(res, indent=2))
