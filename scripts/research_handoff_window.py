
import os
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Metadata
RUN_ID = "handoff_window_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
LOGS_DIR = OUTPUT_ROOT / "logs"
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_job(cmd, job_id):
    with open(f"{LOGS_DIR}/{job_id}.stdout.log", "w") as f_out, \
         open(f"{LOGS_DIR}/{job_id}.stderr.log", "w") as f_err:
        subprocess.run(cmd, stdout=f_out, stderr=f_err)

def run_handoff_sweep():
    # Sweep s_duration (forcing window)
    s_durations = [100, 500, 1000, 2000, 3000, 4000, 5000]
    kappa_vals = [0.5, 0.8, 1.0]
    seeds = [42] # Use same seed to compare windows directly
    jobs = []
    
    for k in kappa_vals:
        for s_dur in s_durations:
            job_id = f"handoff_k_{k}_sdur_{s_dur}"
            out_dir = JOBS_DIR / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            
            # Total steps 25000 to see long-term behavior
            config = {
                "nx": 128,
                "steps": 25000,
                "s": 0.15, # Super-critical
                "s_duration": s_dur,
                "kappa": k,
                "lambda_R": 0.8,
                "initial_condition": {
                    "epsilon_kind": "uniform",
                    "epsilon_base": 0.0,
                    "noise_std": 0.01,
                    "seed": 1
                }
            }
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
            jobs.append((cmd, job_id, k, s_dur))
            
    print(f"Starting {len(jobs)} handoff window jobs...")
    # Sequential to avoid GPU contention if using GPU, but let's try parallel 2
    with ThreadPoolExecutor(max_workers=2) as executor:
        for j in jobs:
            executor.submit(run_job, j[0], j[1])
            
    results = []
    for j in jobs:
        out_dir = JOBS_DIR / j[1]
        summary_path = out_dir / "summary.json"
        if summary_path.exists():
            d = json.load(open(summary_path))
            results.append({
                "kappa": j[2],
                "s_duration": j[3],
                "final_active_fraction": d["final_metrics"]["epsilon_active_fraction"]
            })
    return results

def main():
    res = run_handoff_sweep()
    df = pd.DataFrame(res)
    df.to_csv(OUTPUT_ROOT / "handoff_results.csv", index=False)
    print("Handoff window study complete.")
    print(df)

if __name__ == "__main__":
    main()
