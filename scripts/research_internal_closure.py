import os
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path

# Metadata
RUN_ID = "research_internal_closure_2026-05-04"
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
    
    # Hypothesis: Stability requires Residue Feedback (Closure)
    # PDE: Vary D_R (Residue Diffusion/Feedback)
    # Agent: Vary R_c (Residue coupling)
    
    for seed in seeds:
        # PDE Persistence Sweep
        for dr in [0.0, 0.05, 0.2]:
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
            
        # Agent Stability Sweep
        for rc in [0.0, 0.1, 0.5]:
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
        cmd = f"python {engine} --config {config_path} --out {out_path}"
        subprocess.run(cmd, shell=True, check=False)
        
        summary_path = out_path / "summary.json"
        if summary_path.exists():
            with open(summary_path, "r") as f:
                data = json.load(f)
                metrics = data.get("final_metrics", {})
                
                # We interpret 'stability' as high alignment/order parameter
                # We interpret 'closure' as survival (metrics remaining high)
                val = metrics.get("alignment_success_rate") if model_type == "pde" else metrics.get("order_parameter")
                residue = metrics.get("residue_mean")
                results.append({
                    "model": model_type, 
                    "feedback_strength": param_val, 
                    "seed": seed, 
                    "stability_metric": val,
                    "residue": residue
                })
    return pd.DataFrame(results)

def main():
    ensure_dirs()
    print("Generating Internal Closure configs...")
    configs = generate_configs()
    
    print(f"Running {len(configs)} Closure jobs...")
    df = run_jobs(configs)
    
    df.to_csv(OUTPUT_ROOT / "closure_raw_results.csv", index=False)
    
    print("Synthesizing Results...")
    summary = df.groupby(["model", "feedback_strength"]).agg(
        stability_mean=("stability_metric", "mean"),
        residue_mean=("residue", "mean"),
        stability_std=("stability_metric", "std")
    ).reset_index()
    
    summary.to_csv(OUTPUT_ROOT / "closure_summary.csv", index=False)
    print(summary)
    
    # Manifest
    manifest = {
        "run_id": RUN_ID,
        "purpose": "Internal Closure and Stability Verification (C4)",
        "models": ["structural_box_sim_cpp", "agent_based_sim_v1_cpp"],
        "independent_measurements": 2,
        "falsification_run": True
    }
    with open(OUTPUT_ROOT / "run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()