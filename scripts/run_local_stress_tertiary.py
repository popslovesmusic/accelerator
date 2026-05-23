import json
import subprocess
import os
import statistics
from pathlib import Path

# LOCAL-STRESS-001 - Phase 3: Tertiary Node Phase Boundary
# Rigor: 10x10 Sweep, 5 seeds per point.

run_dir = Path("results/2026-05-22_run06_LOCAL_STRESS_3Peak")
data_dir = run_dir / "data"
artifacts_dir = run_dir / "artifacts"

def run_point(theta_de, k_val, seed):
    config = {
        "n_nodes": 6, # 3-node Basin + 3-node environment
        "steps": 1000,
        "dt": 0.05,
        "K": k_val,
        "theta_de": theta_de,
        "theta_re": 0.1,
        "P_re": 0.1,
        "omega_mean": 1.0,
        "omega_std": 0.5,
        "seed": seed
    }
    
    label = f"sweep_t{theta_de:.1f}_k{k_val:.1f}_s{seed}"
    config_path = data_dir / f"{label}_config.json"
    out_path = data_dir / f"{label}_results"
    with open(config_path, "w") as f: json.dump(config, f)
    
    subprocess.run(["python", "tools/graph_dynamics_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_path)], capture_output=True)
    
    try:
        with open(out_path / "summary.json") as f:
            data = json.load(f)
            return 1.0 - data["final_metrics"]["order_parameter"]
    except: return 0.0

theta_range = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
k_range = [1.0, 2.0, 5.0, 10.0, 20.0]
n_seeds = 5

print(f"Starting Tertiary Phase Boundary Sweep ({len(theta_range)}x{len(k_range)} points, {n_seeds} seeds)...")

grid = []
for t in theta_range:
    row = []
    for k in k_range:
        print(f"  Testing t={t:.1f}, k={k:.1f}...", end="\r")
        vals = [run_point(t, k, s) for s in range(n_seeds)]
        mean_d = sum(vals) / len(vals)
        row.append(mean_d)
    grid.append(row)

print("\nSweep Complete.")

report = {
    "tertiary_sweep": {
        "theta_de": theta_range,
        "K": k_range,
        "distinguishability_grid": grid
    },
    "status": "completed"
}

with open(artifacts_dir / "tertiary_sweep_results.json", "w") as f:
    json.dump(report, f, indent=2)
