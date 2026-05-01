import os
import json
import subprocess
import pandas as pd
import numpy as np
import datetime

# Metadata
RUN_ID = "research_emergence_threshold_2026-05-01"
OUTPUT_ROOT = f"outputs/runs/{RUN_ID}"
LOGS_DIR = f"{OUTPUT_ROOT}/logs"
JOBS_DIR = f"{OUTPUT_ROOT}/jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_pde_threshold():
    # Parameters
    kappa_vals = [0.01, 0.5] # Low vs High residue
    D_eps_vals = [0.01, 0.1] # Tight vs Stable coupling (reduced from 1.0)
    seeds = [10, 11, 12]
    
    results = []
    
    with open("configs/examples/pde_floor_base.json", "r") as f:
        base_config = json.load(f)
    
    for k in kappa_vals:
        for D in D_eps_vals:
            for seed in seeds:
                job_id = f"pde_k_{k}_D_{D}_seed_{seed}"
                out_dir = f"{JOBS_DIR}/{job_id}"
                os.makedirs(out_dir, exist_ok=True)
                
                config = json.loads(json.dumps(base_config))
                config["grid"]["dt"] = 0.001 # Reduced for stability
                config["model"]["kappa"] = k
                config["model"]["D_epsilon"] = D
                config["initial_condition"]["seed"] = seed
                config["output_dir"] = out_dir
                
                config_path = f"{out_dir}/config.json"
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
                
                print(f"[{datetime.datetime.now()}] [PDE] Running k={k}, D={D}, seed={seed}")
                cmd = ["python", "tools/structural_box_sim_v2/sim.py", "--config", config_path, "--out", out_dir]
                
                with open(f"{LOGS_DIR}/{job_id}.stdout.log", "w") as f_out, \
                     open(f"{LOGS_DIR}/{job_id}.stderr.log", "w") as f_err:
                    subprocess.run(cmd, stdout=f_out, stderr=f_err)
                
                # Metrics extracted from nested output path as discovered in previous task
                summary_path = f"{out_dir}/{out_dir}/summary.json"
                if os.path.exists(summary_path):
                    with open(summary_path, "r") as f:
                        summary = json.load(f)
                    metrics = summary["final"]
                    results.append({
                        "mechanism": "pde",
                        "kappa": k,
                        "D_epsilon": D,
                        "seed": seed,
                        "epsilon_mean": metrics["epsilon_mean"],
                        "epsilon_max": metrics["epsilon_max"],
                        "localization_ratio": metrics["epsilon_max"] / metrics["epsilon_mean"] if metrics["epsilon_mean"] > 0 else 0,
                        "output_dir": out_dir
                    })
    return results

def run_abm_threshold():
    # Parameters
    kappa_vals = [0.01, 0.1]
    Rc_vals = [0.5, 2.0]
    seeds = [1, 2, 3]
    
    results = []
    
    for k in kappa_vals:
        for Rc in Rc_vals:
            for seed in seeds:
                job_id = f"abm_k_{k}_Rc_{Rc}_seed_{seed}"
                out_dir = f"{JOBS_DIR}/{job_id}"
                os.makedirs(out_dir, exist_ok=True)
                
                config = {
                    "n_agents": 1000,
                    "steps": 1000,
                    "dt": 0.05,
                    "R_c": Rc,
                    "K_phi": 0.5,
                    "kappa": k,
                    "omega_mean": 1.0,
                    "omega_std": 0.1,
                    "residue_decay": 0.001,
                    "mismatch_rate": 0.05,
                    "seed": seed
                }
                config_path = f"{out_dir}/config.json"
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
                
                print(f"[{datetime.datetime.now()}] [ABM] Running k={k}, Rc={Rc}, seed={seed}")
                cmd = ["python", "tools/agent_based_sim_v1/sim.py", "--config", config_path, "--out", out_dir]
                
                with open(f"{LOGS_DIR}/{job_id}.stdout.log", "w") as f_out, \
                     open(f"{LOGS_DIR}/{job_id}.stderr.log", "w") as f_err:
                    subprocess.run(cmd, stdout=f_out, stderr=f_err)
                
                summary_path = f"{out_dir}/summary.json"
                if os.path.exists(summary_path):
                    with open(summary_path, "r") as f:
                        summary = json.load(f)
                    metrics = summary["final_metrics"]
                    results.append({
                        "mechanism": "abm",
                        "kappa": k,
                        "R_c": Rc,
                        "seed": seed,
                        "order_parameter": metrics["order_parameter"],
                        "mismatch_mean": metrics["mismatch_mean"],
                        "output_dir": out_dir
                    })
    return results

def main():
    print(f"Starting Emergence Threshold Research Run: {RUN_ID}")
    
    pde_results = run_pde_threshold()
    abm_results = run_abm_threshold()
    
    # Save results
    pd.DataFrame(pde_results).to_csv(f"{OUTPUT_ROOT}/pde_threshold_results.csv", index=False)
    pd.DataFrame(abm_results).to_csv(f"{OUTPUT_ROOT}/abm_threshold_results.csv", index=False)
    
    manifest = {
        "run_id": RUN_ID,
        "timestamp": datetime.datetime.now().isoformat(),
        "pde_runs": len(pde_results),
        "abm_runs": len(abm_results),
        "status": "completed"
    }
    with open(f"{OUTPUT_ROOT}/run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Research run complete. Results saved to {OUTPUT_ROOT}")

if __name__ == "__main__":
    main()
