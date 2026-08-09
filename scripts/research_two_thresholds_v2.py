
import os
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Metadata
RUN_ID = "two_threshold_rectification_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
LOGS_DIR = OUTPUT_ROOT / "logs"
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_job(cmd, job_id):
    print(f"Starting {job_id}...")
    with open(f"{LOGS_DIR}/{job_id}.stdout.log", "w") as f_out, \
         open(f"{LOGS_DIR}/{job_id}.stderr.log", "w") as f_err:
        subprocess.run(cmd, stdout=f_out, stderr=f_err)
    print(f"Finished {job_id}.")

# 1. Phase 1: Finer Initiation Sweep (PDE)
def run_finer_s_sweep():
    s_vals = [0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
    seeds = [1, 2, 3]
    jobs = []
    for s in s_vals:
        for seed in seeds:
            job_id = f"pde_init_finer_s_{s}_seed_{seed}"
            out_dir = JOBS_DIR / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            if (out_dir / "summary.json").exists(): continue
            config = {
                "nx": 128, "steps": 5000, "s": s, "kappa": 0.6, "lambda_R": 0.8,
                "initial_condition": {"epsilon_kind": "uniform", "epsilon_base": 0.0, "noise_std": 0.01, "seed": seed}
            }
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f: json.dump(config, f, indent=2)
            cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
            jobs.append((cmd, job_id, out_dir, s, seed))
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        for j in jobs: executor.submit(run_job, j[0], j[1])
    
    results = []
    # Collect all summaries including existing ones
    for s in s_vals:
        for seed in seeds:
            out_dir = JOBS_DIR / f"pde_init_finer_s_{s}_seed_{seed}"
            summary_path = out_dir / "summary.json"
            if summary_path.exists():
                d = json.load(open(summary_path))
                results.append({"mechanism": "pde", "type": "initiation_finer", "s": s, "kappa": 0.6, "seed": seed, "active_fraction": d["final_metrics"]["epsilon_active_fraction"]})
    return results

# 2. Phase 2: True Persistence Threshold (Long Duration PDE)
def run_long_pers_sweep():
    kappa_vals = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0] # Coarser but long
    seeds = [42, 43, 44]
    jobs = []
    for k in kappa_vals:
        for seed in seeds:
            job_id = f"pde_pers_long_k_{k}_seed_{seed}"
            out_dir = JOBS_DIR / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            if (out_dir / "summary.json").exists(): continue
            config = {"nx": 128, "steps": 100000, "kappa": k, "s": 0.01, "seed": seed}
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f: json.dump(config, f, indent=2)
            cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
            jobs.append((cmd, job_id, out_dir, k, seed))

    # Sequential to avoid GPU contention
    for j in jobs:
        run_job(j[0], j[1])
    
    results = []
    for k in kappa_vals:
        for seed in seeds:
            out_dir = JOBS_DIR / f"pde_pers_long_k_{k}_seed_{seed}"
            summary_path = out_dir / "summary.json"
            if summary_path.exists():
                d = json.load(open(summary_path))
                fals_res = d["report"]["falsification_zero_s"]
                results.append({"mechanism": "pde", "type": "persistence_long", "s": 0.0, "kappa": k, "seed": seed, "active_fraction": fals_res["epsilon_active_fraction"]})
    return results

# 3. Phase 3: 2D Decoupling Grid (PDE)
def run_2d_grid():
    s_vals = [0.0, 0.1, 0.2]
    kappa_vals = [0.0, 0.5, 1.0]
    jobs = []
    for s in s_vals:
        for k in kappa_vals:
            job_id = f"pde_grid_s_{s}_k_{k}"
            out_dir = JOBS_DIR / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            if (out_dir / "summary.json").exists(): continue
            config = {
                "nx": 128, "steps": 20000, "s": s, "kappa": k, "lambda_R": 0.8,
                "initial_condition": {"epsilon_kind": "uniform", "epsilon_base": 0.0, "noise_std": 0.01, "seed": 42}
            }
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f: json.dump(config, f, indent=2)
            cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
            jobs.append((cmd, job_id, out_dir, s, k))

    for j in jobs:
        run_job(j[0], j[1])

    results = []
    for s in s_vals:
        for k in kappa_vals:
            out_dir = JOBS_DIR / f"pde_grid_s_{s}_k_{k}"
            summary_path = out_dir / "summary.json"
            if summary_path.exists():
                d = json.load(open(summary_path))
                results.append({"mechanism": "pde", "type": "grid_2d", "s": s, "kappa": k, "seed": 42, "active_fraction": d["final_metrics"]["epsilon_active_fraction"]})
    return results

# 4. Phase 4: Variance Characterization (Agent)
def run_agent_variance():
    kappa_vals = [0.0, 0.05, 0.1, 0.2]
    seeds = list(range(201, 211)) # New seeds
    jobs = []
    for k in kappa_vals:
        for seed in seeds:
            job_id = f"abm_variance_k_{k}_seed_{seed}"
            out_dir = JOBS_DIR / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            if (out_dir / "summary.json").exists(): continue
            config = {
                "agent_count": 500, "steps": 1000, "dt": 0.05, "R_c": 1.0, "K_phi": 0.5,
                "kappa": k, "omega_mean": 1.0, "omega_std": 0.1, "residue_decay": 0.01,
                "mismatch_rate": 0.02, "seed": seed
            }
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f: json.dump(config, f, indent=2)
            cmd = ["python", "tools/agent_based_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
            jobs.append((cmd, job_id, out_dir, k, seed))

    with ThreadPoolExecutor(max_workers=4) as executor:
        for j in jobs: executor.submit(run_job, j[0], j[1])

    results = []
    for k in kappa_vals:
        for seed in seeds:
            out_dir = JOBS_DIR / f"abm_variance_k_{k}_seed_{seed}"
            summary_path = out_dir / "summary.json"
            if summary_path.exists():
                d = json.load(open(summary_path))
                results.append({"mechanism": "agent", "type": "variance_study", "s": np.nan, "mismatch_rate": 0.02, "kappa": k, "seed": seed, "active_fraction": d["final_metrics"]["order_parameter"]})
    return results

def main():
    print(f"Starting Two-Threshold Rectification Run: {RUN_ID}")
    
    res1 = run_finer_s_sweep()
    print("Phase 1 complete.")
    res2 = run_long_pers_sweep()
    print("Phase 2 complete.")
    res3 = run_2d_grid()
    print("Phase 3 complete.")
    res4 = run_agent_variance()
    print("Phase 4 complete.")
    
    all_results = res1 + res2 + res3 + res4
    df = pd.DataFrame(all_results)
    df.to_csv(OUTPUT_ROOT / "raw_rectification_results.csv", index=False)
    
    group_cols = ["mechanism", "type", "s", "kappa"]
    summary_df = df.groupby(group_cols, dropna=False).agg({"active_fraction": ["mean", "std", "count"]}).reset_index()
    summary_df.to_csv(OUTPUT_ROOT / "summary_rectification_results.csv", index=False)
    
    print(f"Research run complete. Results saved to {OUTPUT_ROOT}")
    print(summary_df)

if __name__ == "__main__":
    main()
