import os
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path

# Metadata
RUN_ID = "research_resolution_uq_2026-05-04"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
JOBS_DIR = OUTPUT_ROOT / "jobs"
LOGS_DIR = OUTPUT_ROOT / "logs"

# Tools
PDE_ENGINE = "tools/structural_box_sim_cpp/sim_governed.py"
AGENT_ENGINE = "tools/agent_based_sim_v1_cpp/sim_governed.py"

def ensure_dirs():
    for d in [OUTPUT_ROOT, JOBS_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def generate_configs():
    configs = []
    seeds = [10, 20, 30, 40, 50]
    
    # PDE Coarse vs Fine
    for nx in [32, 512]:
        for seed in seeds:
            cfg = {
                "nx": nx,
                "steps": 500,
                "s": 0.15,
                "initial_condition": {"seed": seed}
            }
            path = JOBS_DIR / f"pde_nx_{nx}_seed_{seed}.json"
            with open(path, "w") as f: json.dump(cfg, f)
            configs.append(("pde", nx, seed, path, OUTPUT_ROOT / f"pde_nx_{nx}_seed_{seed}"))
            
    # Agent Coarse vs Fine
    for count in [100, 1600]:
        for seed in seeds:
            cfg = {
                "agent_count": count,
                "steps": 500,
                "R_c": 0.1,
                "K_phi": 0.6,
                "seed": seed
            }
            path = JOBS_DIR / f"agent_count_{count}_seed_{seed}.json"
            with open(path, "w") as f: json.dump(cfg, f)
            configs.append(("agent", count, seed, path, OUTPUT_ROOT / f"agent_count_{count}_seed_{seed}"))
            
    return configs

def run_jobs(configs):
    results = []
    for model_type, res, seed, config_path, out_path in configs:
        engine = PDE_ENGINE if model_type == "pde" else AGENT_ENGINE
        cmd = f"python {engine} --config {config_path} --out {out_path}"
        subprocess.run(cmd, shell=True, check=False)
        
        summary_path = out_path / "summary.json"
        if summary_path.exists():
            with open(summary_path, "r") as f:
                data = json.load(f)
                metrics = data.get("final_metrics", {})
                val = metrics.get("alignment_success_rate") if model_type == "pde" else metrics.get("order_parameter")
                results.append({"model": model_type, "resolution": res, "seed": seed, "metric_value": val})
    return pd.DataFrame(results)

def main():
    ensure_dirs()
    print("Generating UQ configs...")
    configs = generate_configs()
    
    print(f"Running {len(configs)} UQ jobs...")
    df = run_jobs(configs)
    
    df.to_csv(OUTPUT_ROOT / "uq_raw_results.csv", index=False)
    
    print("Calculating Uncertainty Metrics...")
    summary = df.groupby(["model", "resolution"]).agg(
        mean=("metric_value", "mean"),
        std=("metric_value", "std"),
        min=("metric_value", "min"),
        max=("metric_value", "max")
    ).reset_index()
    
    summary.to_csv(OUTPUT_ROOT / "uq_summary.csv", index=False)
    print(summary)
    
    # Save manifest
    manifest = {
        "run_id": RUN_ID,
        "purpose": "Uncertainty Quantification (C5)",
        "models": ["structural_box_sim_cpp", "agent_based_sim_v1_cpp"],
        "seeds": 5,
        "falsification_run": False
    }
    with open(OUTPUT_ROOT / "run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()