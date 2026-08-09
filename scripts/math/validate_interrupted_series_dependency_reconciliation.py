import json
import os
from datetime import datetime

def validate_dependency_reconciliation():
    registry_path = "registry/math/interrupted_series_dependency_reconciliation_registry.json"
    doc_path = "docs/math/interrupted_series_dependency_reconciliation_audit.md"
    result_path = "validation/results/interrupted_series_dependency_reconciliation_result.json"
    val_out_path = "validation/results/interrupted_series_dependency_reconciliation_validation_result.json"
    
    report = {
        "validation_id": "VAL-DEP-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "families_verified": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing reconciliation registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing reconciliation documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("reconciliation audit results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in results")
            
            if data["governance"]["scope_status"] != "STRICTLY_LOCAL_RESTRICTED_DOMAIN":
                 report["status"] = "fail"
                 report["governance_violations"].append("invalid scope status in results")

            # Check if families are processed
            if not data.get("families_audited"):
                 report["status"] = "fail"
                 report["governance_violations"].append("no families found in audit results")
            else:
                 report["families_verified"] = len(data["families_audited"])

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "pressure points"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_dependency_reconciliation()
    print(json.dumps(res, indent=2))
