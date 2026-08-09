import json
import os
from datetime import datetime

def validate_taxonomy():
    registry_path = "registry/math/unresolved_structure_taxonomy_registry.json"
    doc_path = "docs/math/unresolved_structure_taxonomy.md"
    result_path = "validation/results/unresolved_structure_taxonomy_result.json"
    val_out_path = "validation/results/unresolved_structure_taxonomy_validation_result.json"
    
    report = {
        "validation_id": "VAL-URS-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "targets_verified": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing taxonomy registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing taxonomy documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("taxonomy results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in results")

            # Classification Enforcement Checks
            for entry in data["classifications"]:
                tax_class = entry["taxonomy_class"]
                res_output = entry["resolution_output"]
                
                # Rule: Scope-limited structures must not be marked as globally resolved
                if tax_class == "URS-SCOPE-LIMITED" and res_output not in ["RES-BOUNDED", "RES-PERMANENTLY-OPEN"]:
                     report["status"] = "fail"
                     report["governance_violations"].append(f"scope violation for {entry['target_id']}: {tax_class} improperly resolved")
                
                # Rule: Quarantined structures must preserve quarantine
                if tax_class == "URS-QUARANTINED" and res_output != "RES-QUARANTINE-REQUIRED":
                     report["status"] = "fail"
                     report["governance_violations"].append(f"quarantine breach for {entry['target_id']}")

                report["targets_verified"] += 1

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "taxonomy classes", "unresolved targets"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_taxonomy()
    print(json.dumps(res, indent=2))
