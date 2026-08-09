import json
import os
from datetime import datetime

def validate_sim_008():
    registry_path = "registry/math/mpf_sim_008_admissibility_recovery_registry.json"
    doc_path = "docs/math/mpf_sim_008_admissibility_recovery_and_reentry_mapping.md"
    result_path = "validation/results/mpf_sim_008_admissibility_recovery_result.json"
    val_out_path = "validation/results/mpf_sim_008_admissibility_recovery_validation_result.json"
    
    report = {
        "validation_id": "VAL-SIM-008-VALID",
        "status": "pass",
        "governance_violations": [],
        "metrics_found": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 008 registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 008 documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("sim 008 results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in sim 008 results")
            
            if data["governance"]["physics_status"] != "NON_PHYSICAL_ANALOG_MODEL":
                 report["status"] = "fail"
                 report["governance_violations"].append("missing non-physical analog model declaration in results")

            # Metric presence checks
            required_metrics = [
                "recovery_probability",
                "reentry_stability_score",
                "false_recovery_flag",
                "proof_eligibility_impact"
            ]
            
            if not data.get("recovery_results"):
                 report["status"] = "fail"
                 report["governance_violations"].append("no recovery results found in sim 008")
            else:
                 first_scenario = data["recovery_results"][0]
                 for metric in required_metrics:
                     if metric in first_scenario:
                          report["metrics_found"].append(metric)
                     else:
                          report["status"] = "fail"
                          report["governance_violations"].append(f"missing required metric {metric} in sim 008 scenarios")

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
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
    res = validate_sim_008()
    print(json.dumps(res, indent=2))
