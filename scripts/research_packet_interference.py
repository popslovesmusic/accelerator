import os
import json
import subprocess
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

RUN_ID = "hysteretic_interference_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
LOGS_DIR = OUTPUT_ROOT / "logs"
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_job(cmd, job_id):
    # cmd is a list. On Windows, we need oneAPI env to run the SYCL binary.
    # Ensure paths use backslashes for cmd.exe
    cmd[0] = str(Path(cmd[0]))
    cmd_str = " ".join([f'"{c}"' if " " in c or "\\" in c or "/" in c else c for c in cmd])
    full_cmd = f'call "C:\\Program Files (x86)\\Intel\\oneAPI\\setvars.bat" > nul && {cmd_str}'
    with open(f"{LOGS_DIR}/{job_id}.stdout.log", "w") as f_out, \
         open(f"{LOGS_DIR}/{job_id}.stderr.log", "w") as f_err:
        subprocess.run(full_cmd, shell=True, stdout=f_out, stderr=f_err)

def build_jobs():
    jobs = []
    # s_tests: we want to find s_crit. Baseline is ~0.10
    s_tests = [0.02, 0.04, 0.06, 0.08, 0.10, 0.12]
    modes = ["baseline", "preconditioned_pos", "preconditioned_neg"]
    seeds = [1, 2, 3]
    
    for mode in modes:
        for s_t in s_tests:
            for seed in seeds:
                # We test both positive and negative B pulses
                for sign in [1, -1]:
                    test_s = s_t * sign
                    job_id = f"{mode}_s_{test_s}_seed_{seed}"
                    out_dir = JOBS_DIR / job_id
                    out_dir.mkdir(parents=True, exist_ok=True)
                    
                    sequence = []
                    if mode == "preconditioned_pos":
                        # Pulse A (+)
                        sequence.append({"steps": 1, "injection": {"amplitude": 0.4, "offset": 0.0}})
                        sequence.append({"steps": 10000, "s": 0.0}) # Wait
                    elif mode == "preconditioned_neg":
                        # Pulse A (-)
                        sequence.append({"steps": 1, "injection": {"amplitude": -0.4, "offset": 0.0}})
                        sequence.append({"steps": 10000, "s": 0.0}) # Wait
                    else:
                        sequence.append({"steps": 10000, "s": 0.0}) # Baseline Wait
                    
                    # Test Pulse B
                    sequence.append({"steps": 1, "injection": {"amplitude": test_s, "offset": 0.0}})
                    sequence.append({"steps": 5000, "s": 0.0}) # Observe
                    
                    config = {
                        "nx": 128, "kappa": 0.6, "lambda_R": 0.8, "u": 0.15,
                        "initial_condition": {"epsilon_kind": "uniform", "epsilon_base": 0.0, "noise_std": 0.001, "seed": seed},
                        "sequence": sequence
                    }
                    config_path = out_dir / "config.json"
                    with open(config_path, "w") as f: json.dump(config, f)
                    
                    # Use the new signed engine
                    cmd = ["tools/structural_box_signed_v1_cpp/box_sim.exe", "--config", str(config_path), "--out", str(out_dir)]
                    jobs.append((cmd, job_id, mode, test_s, seed))
    return jobs

def main():
    jobs = build_jobs()
    print(f"Starting {len(jobs)} interference jobs...")
    with ThreadPoolExecutor(max_workers=6) as executor:
        for j in jobs:
            executor.submit(run_job, j[0], j[1])
            
    results = []
    for j in jobs:
        cmd, job_id, mode, s_test, seed = j
        out_dir = JOBS_DIR / job_id
        summary_path = out_dir / "summary.json"
        if summary_path.exists():
            d = json.load(open(summary_path))
            # We measure max epsilon as a sign of activation
            # In signed model, activation could be positive or negative
            e_max = d["final_metrics"]["epsilon_max"]
            results.append({
                "mode": mode, "s_test": s_test, "seed": seed, "epsilon_max": e_max
            })
            
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_ROOT / "interference_results.csv", index=False)
    summary = df.groupby(["mode", "s_test"]).mean().reset_index()
    print(summary)

if __name__ == "__main__":
    main()
