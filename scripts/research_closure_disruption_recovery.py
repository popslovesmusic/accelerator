import os
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path

# Metadata
RUN_ID = "research_closure_disruption_recovery_2026-05-04"
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
    seeds = [10, 20, 30]
    
    for seed in seeds:
        # Disruption Axis: Recovery from Noise Burst (PDE)
        for dr in [0.0, 0.5]:
            cfg = {
                "nx": 128,
                "steps": 2000,
                "s": 0.15,
                "model": {
                    "D_R": dr,
                    "noise_std": 0.5 # High noise burst at start
                },
                "initial_condition": {"seed": seed}
            }
            path = JOBS_DIR / f"pde_disrupt_dr_{dr}_seed_{seed}.json"
            with open(path, "w") as f: json.dump(cfg, f)
            configs.append(("pde", dr, seed, path, OUTPUT_ROOT / f"pde_dr_{dr}_seed_{seed}"))
            
        # Disruption Axis: Recovery from Parameter Dropout (Agent)
        for rc in [0.0, 0.5]:
            cfg = {
                "agent_count": 400,
                "steps": 2000,
                "R_c": rc,
                "K_phi": 0.3, # Start in weak coupling (disrupted state)
                "seed": seed
            }
            path = JOBS_DIR / f"agent_disrupt_rc_{rc}_seed_{seed}.json"
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
                
                # We measure the final stabilized value after 2000 steps
                # Recovery = ability to reach high stability despite high initial noise/weak coupling
                val = metrics.get("alignment_success_rate") if model_type == "pde" else metrics.get("order_parameter")
                results.append({
                    "model": model_type, 
                    "feedback": param_val, 
                    "seed": seed, 
                    "recovery_coherence": val
                })
    return pd.DataFrame(results)

def main():
    ensure_dirs()
    configs = generate_configs()
    print(f"Running {len(configs)} Disruption/Recovery jobs...")
    df = run_jobs(configs)
    
    df.to_csv(OUTPUT_ROOT / "recovery_raw_results.csv", index=False)
    summary = df.groupby(["model", "feedback"]).agg(
        recovery_mean=("recovery_coherence", "mean"),
        recovery_std=("recovery_coherence", "std")
    ).reset_index()
    
    summary.to_csv(OUTPUT_ROOT / "recovery_summary.csv", index=False)
    print(summary)

if __name__ == "__main__":
    main()