import json
import os
from datetime import datetime

def validate_sim_012():
    registry_path = "registry/math/mpf_sim_012_constraint_geology_atlas_registry.json"
    doc_path = "docs/math/mpf_sim_012_constraint_geology_atlas.md"
    result_path = "validation/results/mpf_sim_012_constraint_geology_atlas_result.json"
    val_out_path = "validation/results/mpf_sim_012_constraint_geology_validation_result.json"
    
    report = {
        "validation_id": "VAL-SIM-012-VALID",
        "status": "pass",
        "governance_violations": [],
        "geology_entries_verified": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 012 registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 012 documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("sim 012 results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in sim 012 results")
            
            if data["governance"]["physics_status"] != "NON_PHYSICAL_ANALOG_MODEL":
                 report["status"] = "fail"
                 report["governance_violations"].append("missing non-physical analog model declaration in results")

            # Content checks
            if not data.get("geology_entries"):
                 report["status"] = "fail"
                 report["governance_violations"].append("no geology entries found in sim 012 atlas")
            else:
                 report["geology_entries_verified"] = len(data["geology_entries"])
                 required_fields = ["entry_id", "geology_class", "proof_eligibility_effect"]
                 for entry in data["geology_entries"]:
                     for field in required_fields:
                         if field not in entry:
                              report["status"] = "fail"
                              report["governance_violations"].append(f"missing field {field} in geology entry {entry.get('entry_id')}")

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "geology classes"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_sim_012()
    print(json.dumps(res, indent=2))
