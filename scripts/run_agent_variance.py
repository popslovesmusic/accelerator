
import os
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Metadata
RUN_ID = "two_threshold_rectification_2026-05-03"
JOBS_DIR = Path(f"outputs/runs/{RUN_ID}/jobs")
LOGS_DIR = Path(f"outputs/runs/{RUN_ID}/logs")

def run_job(cmd, job_id):
    with open(f"{LOGS_DIR}/{job_id}.stdout.log", "w") as f_out, \
         open(f"{LOGS_DIR}/{job_id}.stderr.log", "w") as f_err:
        subprocess.run(cmd, stdout=f_out, stderr=f_err)

def run_agent_variance():
    kappa_vals = [0.0, 0.05, 0.1, 0.2]
    seeds = list(range(301, 311)) # Different range to avoid collision
    jobs = []
    for k in kappa_vals:
        for seed in seeds:
            job_id = f"abm_variance_k_{k}_seed_{seed}"
            out_dir = JOBS_DIR / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            config = {
                "agent_count": 500, "steps": 1000, "dt": 0.05, "R_c": 1.0, "K_phi": 0.5,
                "kappa": k, "omega_mean": 1.0, "omega_std": 0.1, "residue_decay": 0.01,
                "mismatch_rate": 0.02, "seed": seed
            }
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f: json.dump(config, f, indent=2)
            cmd = ["python", "tools/agent_based_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
            jobs.append((cmd, job_id))

    print(f"Starting {len(jobs)} Agent variance jobs...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        for j in jobs: executor.submit(run_job, j[0], j[1])
    print("Agent variance study complete.")

if __name__ == "__main__":
    run_agent_variance()
