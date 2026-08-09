import os
import json
import subprocess
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np

RUN_ID = "hysteretic_interference_abm_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(JOBS_DIR, exist_ok=True)

def run_job(cmd, job_id, out_dir):
    with open(out_dir / "stdout.log", "w") as f_out, \
         open(out_dir / "stderr.log", "w") as f_err:
        subprocess.run(cmd, stdout=f_out, stderr=f_err)

def build_jobs():
    jobs = []
    # Test a range that spans the barrier
    m_tests = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03]
    modes = ["baseline", "preconditioned_0", "preconditioned_pi"]
    seeds = [1, 2, 3]
    
    for mode in modes:
        for m_t in m_tests:
            for seed in seeds:
                for test_phi in [0.0, np.pi]:
                    job_id = f"{mode}_m_{m_t}_phi_{test_phi:.2f}_seed_{seed}"
                    out_dir = JOBS_DIR / job_id
                    out_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Clean up old summary to force re-run
                    if (out_dir / "summary.json").exists():
                        os.remove(out_dir / "summary.json")
                    
                    sequence = []
                    if mode == "preconditioned_0":
                        # Pulse A at 0 rad
                        sequence.append({"steps": 1000, "mismatch_rate": 0.05, "mismatch_phase": 0.0, "bias_strength": 0.8})
                        sequence.append({"steps": 1000, "mismatch_rate": 0.0}) # Decay
                    elif mode == "preconditioned_pi":
                        # Pulse A at pi rad
                        sequence.append({"steps": 1000, "mismatch_rate": 0.05, "mismatch_phase": np.pi, "bias_strength": 0.8})
                        sequence.append({"steps": 1000, "mismatch_rate": 0.0}) # Decay
                    else:
                        sequence.append({"steps": 2000, "mismatch_rate": 0.0}) # Baseline
                    
                    # Pulse B
                    sequence.append({"steps": 1000, "mismatch_rate": m_t, "mismatch_phase": test_phi, "bias_strength": 0.8})
                    
                    config = {
                        "agent_count": 1000, "dt": 0.02, "seed": seed,
                        "kappa": 0.6, "K_phi": 1.2, "R_c": 0.8,
                        "sequence": sequence
                    }
                    config_path = out_dir / "config.json"
                    with open(config_path, "w") as f: json.dump(config, f)
                    
                    cmd = ["python", "tools/agent_based_signed_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
                    jobs.append((cmd, job_id, mode, m_t, test_phi, seed, out_dir))
    return jobs

def main():
    jobs = build_jobs()
    print(f"Starting {len(jobs)} ABM interference jobs...")
    with ThreadPoolExecutor(max_workers=6) as executor:
        for j in jobs:
            executor.submit(run_job, j[0], j[1], j[6])
            
    print("Jobs submitted. Wait for completion...")

if __name__ == "__main__":
    main()
