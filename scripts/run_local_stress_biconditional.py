import json
import subprocess
import os
from pathlib import Path

# LOCAL-STRESS-001 - Phase 4: Biconditional Scaling Law
# Rigor: Scale sweep N=12 to 128, 5 seeds each.

run_dir = Path("results/2026-05-22_run06_LOCAL_STRESS_3Peak")
data_dir = run_dir / "data"
artifacts_dir = run_dir / "artifacts"

def run_scale(n_nodes, seed):
    config = {
        "n_nodes": n_nodes,
        "steps": 2000,
        "dt": 0.05,
        "K": 2.5,
        "theta_de": 0.5,
        "theta_re": 0.5,
        "P_re": 0.5, # Active rewiring
        "omega_mean": 1.0,
        "omega_std": 0.5,
        "seed": seed
    }
    
    label = f"scale_n{n_nodes}_s{seed}"
    config_path = data_dir / f"{label}_config.json"
    out_path = data_dir / f"{label}_results"
    with open(config_path, "w") as f: json.dump(config, f)
    
    subprocess.run(["python", "tools/graph_dynamics_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_path)], capture_output=True)
    
    try:
        with open(out_path / "summary.json") as f:
            data = json.load(f)
            return data["final_metrics"]
    except: return {}

scales = [12, 32, 64, 128]
n_seeds = 5

print(f"Starting Biconditional Scaling Sweep ({len(scales)} scales, {n_seeds} seeds)...")

results = []
for n in scales:
    print(f"  Testing N={n}...", end="\r")
    scale_metrics = [run_scale(n, s) for s in range(n_seeds)]
    # Average metrics
    avg_op = sum(m.get("order_parameter", 0) for m in scale_metrics) / n_seeds
    avg_degree = sum(m.get("avg_degree", 0) for m in scale_metrics) / n_seeds
    results.append({
        "n_nodes": n,
        "avg_op": avg_op,
        "avg_degree": avg_degree
    })

print("\nScaling Sweep Complete.")

report = {
    "scaling_sweep": results,
    "status": "completed"
}

with open(artifacts_dir / "scaling_results.json", "w") as f:
    json.dump(report, f, indent=2)
