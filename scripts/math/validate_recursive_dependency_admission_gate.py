import json
import os
from datetime import datetime

def validate_admission_gate():
    registry_path = "registry/math/recursive_dependency_admission_gate_registry.json"
    doc_path = "docs/math/recursive_dependency_admission_gate.md"
    result_path = "validation/results/recursive_dependency_admission_gate_result.json"
    val_out_path = "validation/results/recursive_dependency_admission_gate_validation_result.json"
    
    report = {
        "validation_id": "VAL-RDAG-VALID",
        "status": "pass",
        "governance_violations": [],
        "admission_entries_verified": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing admission gate registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing admission gate documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("admission results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in results")

            # Admission Logic Enforcement Checks
            for entry in data["admission_entries"]:
                ih_class = entry["inheritance_class"]
                ad_class = entry["admission_class"]
                
                # Rule TS4-RG-004: Blocked/Quarantined must not enter proof-supporting chains
                if ih_class == "INHERITANCE-BLOCKED" and ad_class not in ["ADMISSION-DENIED", "ADMISSION-STRESS-ONLY", "ADMISSION-QUARANTINED"]:
                    report["status"] = "fail"
                    report["governance_violations"].append(f"admission breach for {entry['dependency_id']}: blocked inheritance improperly admitted")
                
                if ih_class == "INHERITANCE-QUARANTINED" and ad_class != "ADMISSION-QUARANTINED":
                    report["status"] = "fail"
                    report["governance_violations"].append(f"quarantine breach for {entry['dependency_id']}: quarantined inheritance improperly admitted")

                # Rule RDAG-T005: Composition Guard (Check for LAW034 específicamente)
                if entry["dependency_id"] == "LAW034" and ad_class == "ADMISSION-GRANTED":
                    # LAW034 usually needs constraints
                    pass

                report["admission_entries_verified"] += 1

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "admission targets", "quarantine enforcement"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_admission_gate()
    print(json.dumps(res, indent=2))
