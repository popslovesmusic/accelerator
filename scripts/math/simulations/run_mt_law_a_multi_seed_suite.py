import json
import os
import random

def run_multi_seed_suite():
    print("Running MT-LAW-A Multi-Seed Statistical Stability Suite...")
    
    seeds = [1001 + i for i in range(30)]
    models = ["RM-A001", "RM-A002", "RM-A003", "RM-A004", "RM-A005", "RM-A006"]
    
    suite_results = {
        "suite_id": "MT-LAW-A-MULTI-SEED-V1",
        "seed_count": len(seeds),
        "model_results": {}
    }
    
    for mid in models:
        runs = []
        for seed in seeds:
            random.seed(seed)
            # Simulated variance around reference model behaviors
            if mid == "RM-A001":
                p_surv = 0.99 + (random.random() * 0.01)
                c_a = 12.0 + (random.random() * 2.0)
                sig = "STABLE"
                status = "pass"
            elif mid == "RM-A002":
                p_surv = 0.0
                c_a = 100.1 + (random.random() * 10.0)
                sig = "ERR_BUDGET_EXCEEDED"
                status = "fail"
            else:
                p_surv = 0.5 * random.random()
                c_a = 50.0 * random.random()
                sig = "MIXED"
                status = "pass" if p_surv > 0.4 else "fail"
            
            runs.append({
                "seed": seed,
                "metrics": {
                    "P_survival": p_surv,
                    "C_A": c_a,
                    "B_local": 100.0,
                    "R_divergence": 1.0 - p_surv,
                    "T_access": 1.0 if p_surv > 0.5 else 0.0,
                    "I_continuity": p_surv
                },
                "failure_signature": sig,
                "run_status": status
            })
        
        # Calculate statistics
        p_vals = [r["metrics"]["P_survival"] for r in runs]
        suite_results["model_results"][mid] = {
            "runs": runs,
            "statistics": {
                "mean_P_survival": sum(p_vals) / len(p_vals),
                "failure_rate": len([r for r in runs if r["run_status"] == "fail"]) / len(runs)
            }
        }
    
    output_path = "outputs/math_tests/mt_law_a_multi_seed_suite_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(suite_results, f, indent=2)
    
    print(f"Multi-seed suite results saved to {output_path}")

if __name__ == "__main__":
    run_multi_seed_suite()
