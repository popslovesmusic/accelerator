
import os
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Metadata
RUN_ID = "hysteresis_admissibility_rectification_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
LOGS_DIR = OUTPUT_ROOT / "logs"
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_job(cmd, job_id):
    with open(f"{LOGS_DIR}/{job_id}.stdout.log", "w") as f_out, \
         open(f"{LOGS_DIR}/{job_id}.stderr.log", "w") as f_err:
        subprocess.run(cmd, stdout=f_out, stderr=f_err)

def run_rectification():
    s_tests = [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14]
    l_r = 0.8 # Fixed for precision
    modes = ["baseline", "preconditioned"]
    seeds = [1, 2, 3]
    
    jobs = []
    
    for mode in modes:
        for s_t in s_tests:
            for seed in seeds:
                job_id = f"{mode}_s_{s_t}_seed_{seed}"
                out_dir = JOBS_DIR / job_id
                out_dir.mkdir(parents=True, exist_ok=True)
                
                sequence = []
                if mode == "preconditioned":
                    sequence.append({"steps": 5000, "s": 0.15})   # Prime
                    sequence.append({"steps": 25000, "s": 0.00})  # Long Collapse
                    sequence.append({"steps": 5000, "s": s_t})    # Test (Longer pulse)
                else:
                    sequence.append({"steps": 30000, "s": 0.00})  # Wait
                    sequence.append({"steps": 5000, "s": s_t})    # Test
                    
                config = {
                    "nx": 128,
                    "kappa": 0.6,
                    "lambda_R": l_r,
                    "initial_condition": {
                        "epsilon_kind": "uniform",
                        "epsilon_base": 0.0,
                        "noise_std": 0.01,
                        "seed": seed
                    },
                    "sequence": sequence
                }
                config_path = out_dir / "config.json"
                with open(config_path, "w") as f: json.dump(config, f, indent=2)
                
                cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
                jobs.append((cmd, job_id, mode, s_t, seed))

    print(f"Starting {len(jobs)} rectification jobs...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        for j in jobs:
            executor.submit(run_job, j[0], j[1])
            
    results = []
    for j in jobs:
        out_dir = JOBS_DIR / j[1]
        summary_path = out_dir / "summary.json"
        if summary_path.exists():
            d = json.load(open(summary_path))
            results.append({
                "mode": j[2],
                "s_test": j[3],
                "seed": j[4],
                "active_fraction": d["final_metrics"]["epsilon_active_fraction"]
            })
    return results

def main():
    res = run_rectification()
    df = pd.DataFrame(res)
    df.to_csv(OUTPUT_ROOT / "hysteresis_rectification_results.csv", index=False)
    summary = df.groupby(["mode", "s_test"]).mean().reset_index()
    print(summary)

if __name__ == "__main__":
    main()
