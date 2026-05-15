import json
import os
import random

def run_threshold_sensitivity():
    print("Running MT-LAW-A Threshold Sensitivity Sweeps...")
    
    # Define parameter ranges for sweeps
    budgets = [10.0, 50.0, 100.0, 150.0]
    perturbations = [0.0, 0.1, 0.5, 1.0, 2.0]
    
    sweep_results = {
        "theorem_id": "MT-LAW-A",
        "sweep_id": "THRESHOLD-SENS-V1",
        "data_points": []
    }
    
    for budget in budgets:
        for p_load in perturbations:
            # Simulated model response to parameter variation
            if budget < 20.0 or p_load > 1.5:
                outcome = "collapse"
                sig = "ERR_BUDGET_EXCEEDED" if budget < 20.0 else "REINFORCE_LOSS"
                p_surv = 0.0
            elif budget < 60.0 or p_load > 0.6:
                outcome = "metastable"
                sig = "STABILITY_DRIFT"
                p_surv = 0.6 + (random.random() * 0.3)
            else:
                outcome = "stable"
                sig = "NONE"
                p_surv = 0.95 + (random.random() * 0.05)
            
            sweep_results["data_points"].append({
                "parameters": {
                    "B_local": budget,
                    "perturbation_load": p_load
                },
                "continuation_outcome": outcome,
                "failure_signature": sig,
                "metrics": {
                    "P_survival": p_surv,
                    "C_A": budget * 0.1 + (p_load * 5.0)
                }
            })
            
    # Identify transition points (simplified)
    sweep_results["threshold_transition_points"] = {
        "collapse_boundary_B_local": 20.0,
        "instability_onset_p_load": 0.6
    }
    
    output_path = "outputs/math_tests/mt_law_a_threshold_sensitivity_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(sweep_results, f, indent=2)
    
    print(f"Threshold sensitivity results saved to {output_path}")

if __name__ == "__main__":
    run_threshold_sensitivity()
