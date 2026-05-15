import json
import os
from datetime import datetime

def validate_impact_audit():
    registry_path = "registry/math/mpf_sim_013_constraint_geology_proof_impact_registry.json"
    doc_path = "docs/math/mpf_sim_013_constraint_geology_proof_impact_audit.md"
    result_path = "validation/results/mpf_sim_013_constraint_geology_proof_impact_result.json"
    val_out_path = "validation/results/mpf_sim_013_constraint_geology_impact_validation_result.json"
    
    report = {
        "validation_id": "VAL-SIM-013-VALID",
        "status": "pass",
        "governance_violations": [],
        "audit_results_verified": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 013 registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 013 documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("sim 013 results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in sim 013 results")
            
            if data["governance"]["scope_status"] != "STRICTLY_LOCAL_RESTRICTED_DOMAIN":
                 report["status"] = "fail"
                 report["governance_violations"].append("invalid scope status in sim 013 results")

            # Content checks
            if not data.get("audit_results"):
                 report["status"] = "fail"
                 report["governance_violations"].append("no audit results found in sim 013 results")
            else:
                 report["audit_results_verified"] = len(data["audit_results"])
                 required_fields = ["audit_entry_id", "impact_class", "proof_eligibility_effect", "globalization_risk_score"]
                 for entry in data["audit_results"]:
                     for field in required_fields:
                         if field not in entry:
                              report["status"] = "fail"
                              report["governance_violations"].append(f"missing field {field} in audit entry {entry.get('audit_entry_id')}")

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "impact classes"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_impact_audit()
    print(json.dumps(res, indent=2))
