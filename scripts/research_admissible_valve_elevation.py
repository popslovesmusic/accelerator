import os
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path

# Metadata
RUN_ID = "elevation_admissible_valve_2026-05-04"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
JOBS_DIR = OUTPUT_ROOT / "jobs"

# Tools
PDE_ENGINE = "tools/structural_box_sim_cpp/sim_governed.py"

def ensure_dirs():
    for d in [OUTPUT_ROOT, JOBS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def generate_configs():
    configs = []
    seeds = [100, 200, 300, 400, 500]
    
    # We test the hypothesis that geometry (R) emerges from gated information (E)
    # A(x) logic is implicit in the coupling u*R and kappa*E
    # We sweep kappa (inscription rate) and u (feedback/geometry pressure)
    
    for seed in seeds:
        for kappa in [0.1, 0.6]: # Inscription strength
            for u in [0.0, 0.3]: # Valve pressure (back-pressure from geometry)
                cfg = {
                    "nx": 256,
                    "steps": 2000,
                    "s": 0.15,
                    "kappa": kappa,
                    "u": u,
                    "initial_condition": {"seed": seed}
                }
                path = JOBS_DIR / f"valve_kappa{kappa}_u{u}_seed_{seed}.json"
                with open(path, "w") as f: json.dump(cfg, f)
                configs.append((kappa, u, seed, path, OUTPUT_ROOT / f"valve_k{kappa}_u{u}_seed_{seed}"))
                
    return configs

def run_jobs(configs):
    results = []
    for kappa, u, seed, config_path, out_path in configs:
        subprocess.run(f"python {PDE_ENGINE} --config {config_path} --out {out_path}", shell=True, check=False)
        
        summary_path = out_path / "summary.json"
        if summary_path.exists():
            with open(summary_path, "r") as f:
                data = json.load(f)
                metrics = data.get("final_metrics", {})
                
                # Mapping user variables
                # epsilon_max -> measure of unresolved mismatch
                # residue_max -> measure of geometric realization (geometry from information)
                # alignment_success_rate -> measure of valve throughput A(x)
                
                results.append({
                    "inscription_kappa": kappa,
                    "valve_pressure_u": u,
                    "seed": seed,
                    "mismatch_E": metrics.get("epsilon_max"),
                    "geometry_R": metrics.get("residue_max"),
                    "valve_throughput_A": metrics.get("alignment_success_rate")
                })
    return pd.DataFrame(results)

def main():
    ensure_dirs()
    configs = generate_configs()
    print(f"Running {len(configs)} Elevation/Valve jobs...")
    df = run_jobs(configs)
    
    df.to_csv(OUTPUT_ROOT / "valve_raw_results.csv", index=False)
    summary = df.groupby(["inscription_kappa", "valve_pressure_u"]).agg(
        E_mean=("mismatch_E", "mean"),
        R_mean=("geometry_R", "mean"),
        A_mean=("valve_throughput_A", "mean"),
        A_std=("valve_throughput_A", "std")
    ).reset_index()
    
    summary.to_csv(OUTPUT_ROOT / "valve_summary.csv", index=False)
    print(summary)
    
    # Claim manifest
    manifest = {
        "run_id": RUN_ID,
        "purpose": "Elevation of Information-Geometry into Admissible Valve Dynamics",
        "models": ["structural_box_sim_cpp"],
        "hypotheses": [
            "Geometry (R) emerges as a constrained memory of mismatch (E)",
            "Stability (A) is the persistent actualization of information throughput"
        ]
    }
    with open(OUTPUT_ROOT / "run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()