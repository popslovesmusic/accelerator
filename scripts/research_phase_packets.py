import os
import json
import subprocess
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

RUN_ID = "phase_packets_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
LOGS_DIR = OUTPUT_ROOT / "logs"
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_job(cmd, job_id):
    with open(f"{LOGS_DIR}/{job_id}.stdout.log", "w") as f_out, \
         open(f"{LOGS_DIR}/{job_id}.stderr.log", "w") as f_err:
        subprocess.run(cmd, stdout=f_out, stderr=f_err)

def build_pde_jobs():
    jobs = []
    s_tests = [0.02, 0.05, 0.10, 0.15]
    seeds = [1, 2, 3]
    # 1. Hysteresis check
    for mode in ["baseline", "preconditioned"]:
        for s_t in s_tests:
            for seed in seeds:
                job_id = f"pde_{mode}_s_{s_t}_seed_{seed}"
                out_dir = JOBS_DIR / job_id
                out_dir.mkdir(parents=True, exist_ok=True)
                sequence = []
                if mode == "preconditioned":
                    sequence.append({"steps": 5000, "s": 0.15})
                    sequence.append({"steps": 10000, "s": 0.00})
                    sequence.append({"steps": 5000, "s": s_t})
                else:
                    sequence.append({"steps": 15000, "s": 0.00})
                    sequence.append({"steps": 5000, "s": s_t})
                
                config = {
                    "nx": 128, "kappa": 0.6, "lambda_R": 0.8,
                    "initial_condition": {"epsilon_kind": "uniform", "epsilon_base": 0.0, "noise_std": 0.01, "seed": seed},
                    "sequence": sequence
                }
                config_path = out_dir / "config.json"
                with open(config_path, "w") as f: json.dump(config, f)
                cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
                jobs.append((cmd, job_id, "pde", mode, s_t, 0.6, seed))
                
    # 2. Persistence/Decoupling Check
    kappa_tests = [0.1, 0.5, 0.9]
    for k in kappa_tests:
        for seed in seeds:
            job_id = f"pde_persistence_k_{k}_seed_{seed}"
            out_dir = JOBS_DIR / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            sequence = [
                {"steps": 5000, "s": 0.15}, # Initiate
                {"steps": 10000, "s": 0.00} # Persist
            ]
            config = {
                "nx": 128, "kappa": k, "lambda_R": 0.8,
                "initial_condition": {"epsilon_kind": "uniform", "epsilon_base": 0.0, "noise_std": 0.01, "seed": seed},
                "sequence": sequence
            }
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f: json.dump(config, f)
            cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
            jobs.append((cmd, job_id, "pde", "persistence", 0.0, k, seed))
            
    return jobs

def build_abm_jobs():
    jobs = []
    seeds = [1, 2, 3]
    m_rates = [0.01, 0.05, 0.10]
    kappas = [0.1, 0.5, 1.0]
    for m in m_rates:
        for k in kappas:
            for seed in seeds:
                job_id = f"abm_m_{m}_k_{k}_seed_{seed}"
                out_dir = JOBS_DIR / job_id
                out_dir.mkdir(parents=True, exist_ok=True)
                config = {
                    "agent_count": 2000, "steps": 500, "dt": 0.01,
                    "kappa": k, "R_c": 1.0, "K_phi": 0.5,
                    "mismatch_rate": m, "residue_decay": 0.1,
                    "seed": seed, "omega_mean": 1.0, "omega_std": 0.1
                }
                config_path = out_dir / "config.json"
                with open(config_path, "w") as f: json.dump(config, f)
                cmd = ["python", "tools/agent_based_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
                jobs.append((cmd, job_id, "abm", "grid_sweep", m, k, seed))
    return jobs

def main():
    jobs = build_pde_jobs() + build_abm_jobs()
    print(f"Executing {len(jobs)} jobs...")
    with ThreadPoolExecutor(max_workers=6) as executor:
        for j in jobs:
            executor.submit(run_job, j[0], j[1])
            
    results = []
    for j in jobs:
        cmd, job_id, model, mode, s_val, k_val, seed = j
        out_dir = JOBS_DIR / job_id
        summary_path = out_dir / "summary.json"
        if summary_path.exists():
            d = json.load(open(summary_path))
            af = d["final_metrics"].get("epsilon_active_fraction", 0.0)
            if model == "abm":
                af = d["final_metrics"].get("order_parameter", 0.0)
            results.append({
                "model": model, "mode": mode, "s_or_mismatch": s_val, "kappa": k_val, "seed": seed, "metric": af
            })
            
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_ROOT / "results.csv", index=False)
    print("Research complete. Summary:")
    print(df.groupby(["model", "mode", "s_or_mismatch", "kappa"]).mean().reset_index())

if __name__ == "__main__":
    main()
