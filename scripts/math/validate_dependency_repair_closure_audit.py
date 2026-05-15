import json
import os
from datetime import datetime

def validate_closure_audit():
    registry_path = "registry/math/dependency_repair_closure_audit_registry.json"
    doc_path = "docs/math/dependency_repair_closure_audit.md"
    result_path = "validation/results/dependency_repair_closure_audit_result.json"
    val_out_path = "validation/results/dependency_repair_closure_audit_validation_result.json"
    
    report = {
        "validation_id": "VAL-DRCA-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "audit_targets_verified": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing closure audit registry")
        return report
    
    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["audit_targets_verified"] = len(registry["closure_audit_targets"])

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing closure audit documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("closure audit results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in results")

            # Integrity checks
            if not data.get("repairs_verified") or not data.get("firewall_verified") or not data.get("admission_verified"):
                 report["status"] = "fail"
                 report["governance_violations"].append("audit failed: not all repair stages are verified as consistent")

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "closure outcomes"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_closure_audit()
    print(json.dumps(res, indent=2))
