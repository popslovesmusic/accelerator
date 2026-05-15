import json
import os
from datetime import datetime

def validate_lifecycle_governance():
    registry_path = "registry/math/unresolved_structure_lifecycle_registry.json"
    doc_path = "docs/math/resolution_lifecycle_governance.md"
    result_path = "validation/results/resolution_lifecycle_governance_result.json"
    val_out_path = "validation/results/resolution_lifecycle_validation_result.json"
    
    report = {
        "validation_id": "VAL-URS-LC-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "states_verified": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing lifecycle registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing lifecycle documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("lifecycle results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in results")

            # Check if state tracking is active
            if not data.get("state_tracking"):
                 report["status"] = "fail"
                 report["governance_violations"].append("no state tracking entries found in results")
            else:
                 report["states_verified"] = len(data["state_tracking"])

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "lifecycle states", "critical transitions"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_lifecycle_governance()
    print(json.dumps(res, indent=2))
