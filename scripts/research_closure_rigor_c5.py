import os
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path

# Metadata
RUN_ID = "research_closure_rigor_c5_2026-05-04"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
JOBS_DIR = OUTPUT_ROOT / "jobs"

# Tools
PDE_ENGINE = "tools/structural_box_sim_cpp/sim_governed.py"
AGENT_ENGINE = "tools/agent_based_sim_v1_cpp/sim_governed.py"

def ensure_dirs():
    for d in [OUTPUT_ROOT, JOBS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def generate_configs():
    configs = []
    # Increased to 20 seeds for C5 rigor
    seeds = list(range(100, 120))
    
    for seed in seeds:
        # PDE Persistence Sweep (High Rigor)
        for dr in [0.0, 0.2]:
            cfg = {
                "nx": 128,
                "steps": 1000,
                "s": 0.15,
                "model": {
                    "D_R": dr
                },
                "initial_condition": {"seed": seed}
            }
            path = JOBS_DIR / f"pde_dr_{dr}_seed_{seed}.json"
            with open(path, "w") as f: json.dump(cfg, f)
            configs.append(("pde", dr, seed, path, OUTPUT_ROOT / f"pde_dr_{dr}_seed_{seed}"))
            
        # Agent Stability Sweep (High Rigor)
        for rc in [0.0, 0.5]:
            cfg = {
                "agent_count": 400,
                "steps": 1000,
                "R_c": rc,
                "K_phi": 0.6,
                "seed": seed
            }
            path = JOBS_DIR / f"agent_rc_{rc}_seed_{seed}.json"
            with open(path, "w") as f: json.dump(cfg, f)
            configs.append(("agent", rc, seed, path, OUTPUT_ROOT / f"agent_rc_{rc}_seed_{seed}"))
            
    return configs

def run_jobs(configs):
    results = []
    for model_type, param_val, seed, config_path, out_path in configs:
        engine = PDE_ENGINE if model_type == "pde" else AGENT_ENGINE
        subprocess.run(f"python {engine} --config {config_path} --out {out_path}", shell=True, check=False)
        
        summary_path = out_path / "summary.json"
        if summary_path.exists():
            with open(summary_path, "r") as f:
                data = json.load(f)
                metrics = data.get("final_metrics", {})
                val = metrics.get("alignment_success_rate") if model_type == "pde" else metrics.get("order_parameter")
                residue = metrics.get("residue_mean")
                results.append({
                    "model": model_type, 
                    "feedback": param_val, 
                    "seed": seed, 
                    "stability": val,
                    "residue": residue
                })
    return pd.DataFrame(results)

def main():
    ensure_dirs()
    configs = generate_configs()
    print(f"Running {len(configs)} high-rigor (C5) jobs...")
    df = run_jobs(configs)
    
    df.to_csv(OUTPUT_ROOT / "rigor_raw_results.csv", index=False)
    summary = df.groupby(["model", "feedback"]).agg(
        stability_mean=("stability", "mean"),
        stability_std=("stability", "std"),
        residue_mean=("residue", "mean")
    ).reset_index()
    
    summary.to_csv(OUTPUT_ROOT / "rigor_summary.csv", index=False)
    print(summary)

if __name__ == "__main__":
    main()