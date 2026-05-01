import os
import json
import subprocess
import pandas as pd
import numpy as np
import datetime

# Metadata
RUN_ID = "research_floor_convergence_2026-05-01"
OUTPUT_ROOT = f"outputs/runs/{RUN_ID}"
LOGS_DIR = f"{OUTPUT_ROOT}/logs"
JOBS_DIR = f"{OUTPUT_ROOT}/jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_ca_floor():
    # Parameters
    residue_growth_vals = [0.1, 0.0] # 0.0 is FV-3
    seeds = [1, 2, 3]
    
    results = []
    
    for rg in residue_growth_vals:
        for seed in seeds:
            job_id = f"ca_extreme_rg_{rg}_seed_{seed}"
            out_dir = f"{JOBS_DIR}/{job_id}"
            os.makedirs(out_dir, exist_ok=True)
            
            # Extreme suppression: low source, stable diffusion
            config = {
                "grid_size": 128,
                "steps": 1000,
                "diffusion_rate": 0.25, # Reduced from 0.5 to prevent overflow
                "residue_growth": rg,
                "residue_decay": 0.04,
                "initial_residue": 0.1,
                "source_strength": 0.1, 
                "seed": seed
            }
            config_path = f"{out_dir}/config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            print(f"[{datetime.datetime.now()}] [CA] Running rg={rg}, seed={seed}")
            cmd = [
                "python", "tools/ca_admissibility_sim_v1/sim.py",
                "--config", config_path,
                "--out", out_dir
            ]
            
            with open(f"{LOGS_DIR}/{job_id}.stdout.log", "w") as f_out, \
                 open(f"{LOGS_DIR}/{job_id}.stderr.log", "w") as f_err:
                subprocess.run(cmd, stdout=f_out, stderr=f_err)
            
            summary_path = f"{out_dir}/summary.json"
            if os.path.exists(summary_path):
                with open(summary_path, "r") as f:
                    summary = json.load(f)
                metrics = summary["final_metrics"]
                results.append({
                    "mechanism": "ca",
                    "param_val": rg,
                    "seed": seed,
                    "active_fraction": metrics["active_fraction"],
                    "mean_mismatch": metrics["mean_mismatch"],
                    "mean_residue": metrics["mean_residue"],
                    "output_dir": out_dir
                })
    return results

def run_pde_floor():
    # Parameters
    kappa_vals = [0.5, 1e-9] # 1e-9 is FV-3 (bypassing strict >0 validation)
    seeds = [10, 11, 12]
    
    results = []
    
    with open("configs/examples/pde_floor_base.json", "r") as f:
        base_config = json.load(f)
    
    for k in kappa_vals:
        for seed in seeds:
            job_id = f"pde_extreme_kappa_{k}_seed_{seed}"
            out_dir = f"{JOBS_DIR}/{job_id}"
            os.makedirs(out_dir, exist_ok=True)
            
            config = json.loads(json.dumps(base_config)) # Deep copy
            config["model"]["kappa"] = k
            config["initial_condition"]["seed"] = seed
            # Note: PDE sim overrides output_dir internally if specified in config, but we pass via CLI
            
            config_path = f"{out_dir}/config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            print(f"[{datetime.datetime.now()}] [PDE] Running kappa={k}, seed={seed}")
            cmd = [
                "python", "tools/structural_box_sim_v2/sim.py",
                "--config", config_path,
                "--out", out_dir
            ]
            
            with open(f"{LOGS_DIR}/{job_id}.stdout.log", "w") as f_out, \
                 open(f"{LOGS_DIR}/{job_id}.stderr.log", "w") as f_err:
                subprocess.run(cmd, stdout=f_out, stderr=f_err)
            
            summary_path = f"{out_dir}/{out_dir}/summary.json"
            if os.path.exists(summary_path):
                with open(summary_path, "r") as f:
                    summary = json.load(f)
                metrics = summary["final"]
                results.append({
                    "mechanism": "pde",
                    "param_val": k,
                    "seed": seed,
                    "epsilon_mean": metrics["epsilon_mean"],
                    "epsilon_max": metrics["epsilon_max"],
                    "residue_mean": metrics["residue_mean"],
                    "epsilon_active_fraction": metrics["epsilon_active_fraction"],
                    "output_dir": out_dir
                })
            else:
                print(f"Warning: No summary found at {summary_path}")

    return results

def main():
    print(f"Starting Governed Research Run: {RUN_ID}")
    
    ca_results = run_ca_floor()
    pde_results = run_pde_floor()
    
    # Save results
    ca_df = pd.DataFrame(ca_results)
    ca_df.to_csv(f"{OUTPUT_ROOT}/ca_floor_results.csv", index=False)
    
    pde_df = pd.DataFrame(pde_results)
    pde_df.to_csv(f"{OUTPUT_ROOT}/pde_floor_results.csv", index=False)
    
    # Generate Run Manifest
    manifest = {
        "run_id": RUN_ID,
        "timestamp": datetime.datetime.now().isoformat(),
        "ca_runs": len(ca_results),
        "pde_runs": len(pde_results),
        "status": "completed"
    }
    with open(f"{OUTPUT_ROOT}/run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Research run complete. Manifest saved to {OUTPUT_ROOT}/run_manifest.json")

if __name__ == "__main__":
    main()
