import json
import os
from datetime import datetime

def validate_sim_011():
    registry_path = "registry/math/mpf_sim_011_admissibility_hysteresis_registry.json"
    doc_path = "docs/math/mpf_sim_011_recursive_admissibility_hysteresis_mapping.md"
    result_path = "validation/results/mpf_sim_011_admissibility_hysteresis_result.json"
    val_out_path = "validation/results/mpf_sim_011_admissibility_hysteresis_validation_result.json"
    
    report = {
        "validation_id": "VAL-SIM-011-VALID",
        "status": "pass",
        "governance_violations": [],
        "metrics_found": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 011 registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 011 documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("sim 011 results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in sim 011 results")
            
            if data["governance"]["physics_status"] != "NON_PHYSICAL_ANALOG_MODEL":
                 report["status"] = "fail"
                 report["governance_violations"].append("missing non-physical analog model declaration in results")

            # Metric presence checks
            required_metrics = [
                "hysteresis_loop_area",
                "recovery_asymmetry_index",
                "scar_irreversibility_score",
                "reset_completeness_score",
                "proof_eligibility_hysteresis"
            ]
            
            if not data.get("hysteresis_results"):
                 report["status"] = "fail"
                 report["governance_violations"].append("no hysteresis results found in sim 011 results")
            else:
                 first_scenario = data["hysteresis_results"][0]
                 for metric in required_metrics:
                     if metric in first_scenario:
                          report["metrics_found"].append(metric)
                     else:
                          report["status"] = "fail"
                          report["governance_violations"].append(f"missing required metric {metric} in sim 011 scenarios")

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "analog_model"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_sim_011()
    print(json.dumps(res, indent=2))
