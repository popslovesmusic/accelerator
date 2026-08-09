
import os
import json
import subprocess
import pandas as pd
import numpy as np
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Metadata
RUN_ID = "two_threshold_rigor_2026-05-03"
OUTPUT_ROOT = f"outputs/runs/{RUN_ID}"
LOGS_DIR = f"{OUTPUT_ROOT}/logs"
JOBS_DIR = f"{OUTPUT_ROOT}/jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_job(cmd, job_id):
    with open(f"{LOGS_DIR}/{job_id}.stdout.log", "w") as f_out, \
         open(f"{LOGS_DIR}/{job_id}.stderr.log", "w") as f_err:
        subprocess.run(cmd, stdout=f_out, stderr=f_err)

def run_pde_initiation_sweep():
    s_vals = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    seeds = [1, 2, 3]
    jobs = []
    
    for s in s_vals:
        for seed in seeds:
            job_id = f"pde_init_s_{s}_seed_{seed}"
            out_dir = Path(JOBS_DIR) / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            
            # Updated to match structural_box_sim_cpp requirements
            config = {
                "nx": 128,
                "steps": 5000,
                "s": s,
                "kappa": 0.6,
                "lambda_R": 0.8,
                "initial_condition": {
                    "epsilon_kind": "uniform", "epsilon_base": 0.0, "noise_std": 0.01, "seed": seed
                }
            }
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
            jobs.append((cmd, job_id, out_dir, s, seed))
            
    with ThreadPoolExecutor(max_workers=4) as executor:
        for j in jobs:
            executor.submit(run_job, j[0], j[1])
            
    results = []
    for j in jobs:
        out_dir = j[2]
        summary_path = out_dir / "summary.json"
        if summary_path.exists():
            with open(summary_path, "r") as f:
                summary = json.load(f)
            results.append({
                "mechanism": "pde", "type": "initiation", "s": j[3], "kappa": 0.6, "seed": j[4],
                "active_fraction": summary["final_metrics"]["epsilon_active_fraction"]
            })
    return results

def run_pde_persistence_sweep():
    kappa_vals = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    seeds = [42, 43, 44]
    jobs = []
    
    for k in kappa_vals:
        for seed in seeds:
            job_id = f"pde_pers_k_{k}_seed_{seed}"
            out_dir = Path(JOBS_DIR) / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            
            config = {"nx": 128, "steps": 50000, "kappa": k, "s": 0.01, "seed": seed}
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
            jobs.append((cmd, job_id, out_dir, k, seed))

    with ThreadPoolExecutor(max_workers=4) as executor:
        for j in jobs:
            executor.submit(run_job, j[0], j[1])

    results = []
    for j in jobs:
        out_dir = j[2]
        summary_path = out_dir / "summary.json"
        if summary_path.exists():
            with open(summary_path, "r") as f:
                summary = json.load(f)
            falsification_res = summary["report"]["falsification_zero_s"]
            results.append({
                "mechanism": "pde", "type": "persistence", "s": 0.0, "kappa": j[3], "seed": j[4],
                "active_fraction": falsification_res["epsilon_active_fraction"]
            })
    return results

def run_agent_sweeps():
    seeds = [1, 2, 3]
    results = []
    
    # 1. Initiation
    mr_vals = [0.0, 0.02, 0.04, 0.06, 0.08, 0.1]
    jobs = []
    for mr in mr_vals:
        for seed in seeds:
            job_id = f"abm_init_mr_{mr}_seed_{seed}"
            out_dir = Path(JOBS_DIR) / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            config = {
                "agent_count": 500, "steps": 1000, "dt": 0.05, "R_c": 1.0, "K_phi": 0.5,
                "kappa": 0.05, "omega_mean": 1.0, "omega_std": 0.1, "residue_decay": 0.01,
                "mismatch_rate": mr, "seed": seed
            }
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            cmd = ["python", "tools/agent_based_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
            jobs.append((cmd, job_id, out_dir, mr, seed))

    with ThreadPoolExecutor(max_workers=4) as executor:
        for j in jobs: executor.submit(run_job, j[0], j[1])
    for j in jobs:
        summary_path = j[2] / "summary.json"
        if summary_path.exists():
            with open(summary_path, "r") as f: summary = json.load(f)
            results.append({"mechanism": "agent", "type": "initiation", "mismatch_rate": j[3], "kappa": 0.05, "seed": j[4], "active_fraction": summary["final_metrics"]["order_parameter"]})

    # 2. Persistence
    kappa_vals = [0.0, 0.01, 0.02, 0.05, 0.1, 0.2]
    jobs = []
    for k in kappa_vals:
        for seed in seeds:
            job_id = f"abm_pers_k_{k}_seed_{seed}"
            out_dir = Path(JOBS_DIR) / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            config = {
                "agent_count": 500, "steps": 1000, "dt": 0.05, "R_c": 1.0, "K_phi": 0.5,
                "kappa": k, "omega_mean": 1.0, "omega_std": 0.1, "residue_decay": 0.01,
                "mismatch_rate": 0.02, "seed": seed
            }
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            cmd = ["python", "tools/agent_based_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
            jobs.append((cmd, job_id, out_dir, k, seed))

    with ThreadPoolExecutor(max_workers=4) as executor:
        for j in jobs: executor.submit(run_job, j[0], j[1])
    for j in jobs:
        summary_path = j[2] / "summary.json"
        if summary_path.exists():
            with open(summary_path, "r") as f: summary = json.load(f)
            results.append({"mechanism": "agent", "type": "persistence", "mismatch_rate": 0.02, "kappa": j[3], "seed": j[4], "active_fraction": summary["final_metrics"]["order_parameter"]})
    return results

def main():
    pde_init = run_pde_initiation_sweep()
    pde_pers = run_pde_persistence_sweep()
    agent_res = run_agent_sweeps()
    
    all_results = pde_init + pde_pers + agent_res
    df = pd.DataFrame(all_results)
    df.to_csv(f"{OUTPUT_ROOT}/raw_results.csv", index=False)
    group_cols = ["mechanism", "type", "s", "kappa", "mismatch_rate"]
    for col in group_cols:
        if col not in df.columns: df[col] = np.nan
    summary_df = df.groupby(group_cols, dropna=False).mean().reset_index()
    summary_df.to_csv(f"{OUTPUT_ROOT}/summary_results.csv", index=False)
    print("Research run complete.")

if __name__ == "__main__":
    main()
