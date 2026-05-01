import os
import json
import subprocess
import pandas as pd
import numpy as np
import datetime

# Metadata
RUN_ID = "research_one_process_stability_2026-05-01"
OUTPUT_ROOT = f"outputs/runs/{RUN_ID}"
LOGS_DIR = f"{OUTPUT_ROOT}/logs"
JOBS_DIR = f"{OUTPUT_ROOT}/jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_ca_sweep():
    # Parameters
    residue_growth_vals = [0.0, 0.01, 0.05, 0.1] # 0.0 is FV-3
    seeds = [1, 2, 3]
    
    results = []
    
    for rg in residue_growth_vals:
        for seed in seeds:
            job_id = f"ca_rg_{rg}_seed_{seed}"
            out_dir = f"{JOBS_DIR}/{job_id}"
            os.makedirs(out_dir, exist_ok=True)
            
            config = {
                "grid_size": 128,
                "steps": 1000,
                "diffusion_rate": 0.1,
                "residue_growth": rg,
                "residue_decay": 0.04,
                "initial_residue": 0.1,
                "source_strength": 1.0,
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

def run_abm_sweep():
    # Parameters
    mismatch_rate_vals = [0.01, 0.05, 0.1]
    kappa_vals = [0.05] # Base
    seeds = [1, 2, 3]
    
    results = []
    
    # 1. Sweep mismatch_rate
    for mr in mismatch_rate_vals:
        for seed in seeds:
            job_id = f"abm_mr_{mr}_seed_{seed}"
            out_dir = f"{JOBS_DIR}/{job_id}"
            os.makedirs(out_dir, exist_ok=True)
            
            config = {
                "n_agents": 1000,
                "steps": 1000,
                "dt": 0.05,
                "R_c": 1.0,
                "K_phi": 0.5,
                "kappa": 0.05,
                "omega_mean": 1.0,
                "omega_std": 0.1,
                "residue_decay": 0.001,
                "mismatch_rate": mr,
                "seed": seed
            }
            config_path = f"{out_dir}/config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            print(f"[{datetime.datetime.now()}] [ABM] Running mr={mr}, seed={seed}")
            cmd = [
                "python", "tools/agent_based_sim_v1/sim.py",
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
                    "mechanism": "abm",
                    "param_val": mr,
                    "seed": seed,
                    "order_parameter": metrics["order_parameter"],
                    "mismatch_mean": metrics["mismatch_mean"],
                    "residue_mean": metrics["residue_mean"],
                    "output_dir": out_dir
                })

    # 2. FV-3: No residue (kappa=0)
    for seed in seeds:
        job_id = f"abm_fv3_kappa_0_seed_{seed}"
        out_dir = f"{JOBS_DIR}/{job_id}"
        os.makedirs(out_dir, exist_ok=True)
        
        config = {
            "n_agents": 1000,
            "steps": 1000,
            "dt": 0.05,
            "R_c": 1.0,
            "K_phi": 0.5,
            "kappa": 0.0,
            "omega_mean": 1.0,
            "omega_std": 0.1,
            "residue_decay": 0.001,
            "mismatch_rate": 0.05,
            "seed": seed
        }
        config_path = f"{out_dir}/config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"[{datetime.datetime.now()}] [ABM] Running FV-3 kappa=0, seed={seed}")
        cmd = [
            "python", "tools/agent_based_sim_v1/sim.py",
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
                "mechanism": "abm_fv3",
                "param_val": 0.0,
                "seed": seed,
                "order_parameter": metrics["order_parameter"],
                "mismatch_mean": metrics["mismatch_mean"],
                "residue_mean": metrics["residue_mean"],
                "output_dir": out_dir
            })
            
    # 3. FV-4: Adversarial Initialization (two_clusters)
    for seed in seeds:
        job_id = f"abm_fv4_init_seed_{seed}"
        out_dir = f"{JOBS_DIR}/{job_id}"
        os.makedirs(out_dir, exist_ok=True)
        
        config = {
            "n_agents": 1000,
            "steps": 2000, # Increased steps for convergence
            "dt": 0.05,
            "R_c": 1.0,
            "K_phi": 1.0, # Increased coupling to overcome gap
            "kappa": 0.05,
            "omega_mean": 1.0,
            "omega_std": 0.1,
            "residue_decay": 0.001,
            "mismatch_rate": 0.05,
            "seed": seed,
            "initial_distribution": "two_clusters"
        }
        config_path = f"{out_dir}/config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"[{datetime.datetime.now()}] [ABM] Running FV-4 adversarial init, seed={seed}")
        cmd = [
            "python", "tools/agent_based_sim_v1/sim.py",
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
                "mechanism": "abm_fv4",
                "param_val": 1.0,
                "seed": seed,
                "order_parameter": metrics["order_parameter"],
                "mismatch_mean": metrics["mismatch_mean"],
                "residue_mean": metrics["residue_mean"],
                "output_dir": out_dir
            })

    return results

def main():
    print(f"Starting Governed Research Run: {RUN_ID}")
    
    ca_results = run_ca_sweep()
    abm_results = run_abm_sweep()
    
    # Save results
    ca_df = pd.DataFrame(ca_results)
    ca_df.to_csv(f"{OUTPUT_ROOT}/ca_results.csv", index=False)
    
    abm_df = pd.DataFrame(abm_results)
    abm_df.to_csv(f"{OUTPUT_ROOT}/abm_results.csv", index=False)
    
    # Generate Run Manifest
    manifest = {
        "run_id": RUN_ID,
        "timestamp": datetime.datetime.now().isoformat(),
        "ca_runs": len(ca_results),
        "abm_runs": len(abm_results),
        "status": "completed"
    }
    with open(f"{OUTPUT_ROOT}/run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Research run complete. Manifest saved to {OUTPUT_ROOT}/run_manifest.json")

if __name__ == "__main__":
    main()
