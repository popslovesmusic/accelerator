import json
import os
from datetime import datetime

def validate_sim_003():
    registry_path = "registry/math/mpf_sim_003_metastability_oscillation_registry.json"
    doc_path = "docs/math/mpf_sim_003_metastability_oscillatory_basin_mapping.md"
    result_path = "validation/results/mpf_sim_003_metastability_oscillation_result.json"
    val_out_path = "validation/results/mpf_sim_003_metastability_oscillation_validation_result.json"
    
    report = {
        "validation_id": "VAL-SIM-003-VALID",
        "status": "pass",
        "governance_violations": [],
        "metrics_found": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 003 registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing sim 003 documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("sim 003 results not yet generated")
    else:
        with open(result_path, 'r') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in sim 003 results")
            
            if data["governance"]["physics_status"] != "NON_PHYSICAL_ANALOG_MODEL":
                 report["status"] = "fail"
                 report["governance_violations"].append("missing non-physical analog model declaration in results")

            # Metric presence checks
            required_metrics = [
                "metastability_score",
                "projection_cycle_period",
                "idempotence_error_envelope",
                "threshold_crossing_count",
                "proof_eligibility_impact"
            ]
            
            if not data.get("scenario_results"):
                 report["status"] = "fail"
                 report["governance_violations"].append("no scenario results found in sim 003")
            else:
                 # Check for false stability trap scenario specifically
                 scenarios = [s["scenario_id"] for s in data["scenario_results"]]
                 if "SIM003-S004" not in scenarios:
                      report["status"] = "fail"
                      report["governance_violations"].append("missing false stability trap scenario in sim 003 results")

                 first_scenario = data["scenario_results"][0]
                 for metric in required_metrics:
                     if metric in first_scenario:
                          report["metrics_found"].append(metric)
                     else:
                          report["status"] = "fail"
                          report["governance_violations"].append(f"missing required metric {metric} in sim 003 scenarios")

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
    res = validate_sim_003()
    print(json.dumps(res, indent=2))
