import os
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path

# Metadata
RUN_ID = "research_pde_closure_threshold_2026-05-04"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
JOBS_DIR = OUTPUT_ROOT / "jobs"

# Tools
PDE_ENGINE = "tools/structural_box_sim_cpp/sim_governed.py"

def ensure_dirs():
    for d in [OUTPUT_ROOT, JOBS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def generate_configs():
    configs = []
    seeds = [10, 20, 30, 40, 50]
    
    # Testing near-threshold forcing s=0.08
    # High feedback (D_R=0.5) should stabilize alignment where low feedback fails
    for seed in seeds:
        for dr in [0.0, 0.5]:
            cfg = {
                "nx": 128,
                "steps": 2000,
                "s": 0.08, 
                "model": {
                    "D_R": dr
                },
                "initial_condition": {"seed": seed}
            }
            path = JOBS_DIR / f"pde_s0.08_dr_{dr}_seed_{seed}.json"
            with open(path, "w") as f: json.dump(cfg, f)
            configs.append(("pde", dr, seed, path, OUTPUT_ROOT / f"pde_dr_{dr}_seed_{seed}"))
            
    return configs

def run_jobs(configs):
    results = []
    for model_type, param_val, seed, config_path, out_path in configs:
        cmd = f"python {PDE_ENGINE} --config {config_path} --out {out_path}"
        subprocess.run(cmd, shell=True, check=False)
        
        summary_path = out_path / "summary.json"
        if summary_path.exists():
            with open(summary_path, "r") as f:
                data = json.load(f)
                metrics = data.get("final_metrics", {})
                val = metrics.get("alignment_success_rate")
                results.append({
                    "feedback_strength": param_val, 
                    "seed": seed, 
                    "alignment": val
                })
    return pd.DataFrame(results)

def main():
    ensure_dirs()
    configs = generate_configs()
    df = run_jobs(configs)
    
    df.to_csv(OUTPUT_ROOT / "pde_threshold_raw.csv", index=False)
    summary = df.groupby("feedback_strength").agg(
        alignment_mean=("alignment", "mean"),
        alignment_std=("alignment", "std")
    ).reset_index()
    
    summary.to_csv(OUTPUT_ROOT / "pde_threshold_summary.csv", index=False)
    print(summary)

if __name__ == "__main__":
    main()