import json
import os
from datetime import datetime

def validate_sim_006():
    registry_path = "registry/math/mpf_sim_006_cross_simulation_evidence_atlas_registry.json"
    doc_path = "docs/math/mpf_sim_006_cross_simulation_evidence_atlas.md"
    result_path = "validation/results/mpf_sim_006_cross_simulation_evidence_atlas_result.json"
    val_out_path = "validation/results/mpf_sim_006_cross_simulation_evidence_atlas_validation_result.json"
    
    report = {
        "validation_id": "VAL-SIM-006-VALID",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 006 registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 006 documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("sim 006 results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Check for governance headers
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in results")
            
            if data["governance"]["physics_status"] != "NON_PHYSICAL_ANALOG_MODEL":
                 report["status"] = "fail"
                 report["governance_violations"].append("missing non-physical analog model declaration in results")

            # Check for required atlas entries
            if not data.get("cross_simulation_entries"):
                 report["status"] = "fail"
                 report["governance_violations"].append("no cross-simulation entries found in atlas results")
            else:
                 required_fields = ["entry_id", "source_simulations", "evidence_class"]
                 for field in required_fields:
                     if field not in data["cross_simulation_entries"][0]:
                          report["status"] = "fail"
                          report["governance_violations"].append(f"missing field {field} in atlas entries")

    # 3. Doc Content Verification
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "analog_model"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_sim_006()
    print(json.dumps(res, indent=2))
