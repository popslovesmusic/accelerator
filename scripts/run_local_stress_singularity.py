import json
import subprocess
import os
import statistics
from pathlib import Path

# LOCAL-STRESS-001 - Phase 2: Singularity Rebound Persistence
# Rigor: 30 seeds, 10,000 steps, extreme K.

run_dir = Path("results/2026-05-22_run06_LOCAL_STRESS_3Peak")
data_dir = run_dir / "data"
artifacts_dir = run_dir / "artifacts"

def get_stats(data):
    if not data or len(data) == 0: return {"mean": 0, "std": 0}
    mean = sum(data) / len(data)
    if len(data) > 1:
        variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
        std = variance ** 0.5
    else:
        std = 0
    return {"mean": mean, "std": std}

def run_rebound_seed(seed):
    config = {
        "n_nodes": 3,
        "steps": 10000, # Deep temporal stress
        "dt": 0.05,
        "K": 50.0,      # Extreme compression
        "theta_de": 0.5,
        "theta_re": 0.5,
        "P_re": 1.0,
        "omega_mean": 1.0,
        "omega_std": 0.5,
        "seed": seed
    }
    
    label = f"rebound_s{seed}"
    config_path = data_dir / f"{label}_config.json"
    out_path = data_dir / f"{label}_results"
    with open(config_path, "w") as f: json.dump(config, f)
    
    subprocess.run(["python", "tools/graph_dynamics_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_path)], capture_output=True)
    
    try:
        with open(out_path / "summary.json") as f:
            data = json.load(f)
            return 1.0 - data["final_metrics"]["order_parameter"]
    except: return 0.0

n_seeds = 30
print(f"Starting Singularity Rebound Persistence Stress ({n_seeds} seeds, 10k steps)...")

rebound_vals = []
for s in range(n_seeds):
    print(f"  Seed {s+1}/{n_seeds}...", end="\r")
    rebound_vals.append(run_rebound_seed(s))

s_rebound = get_stats(rebound_vals)

print(f"\nRebound Stress Complete.")
print(f"  Mean Distinguishability Floor (D): {s_rebound['mean']:.6f}")
print(f"  Std Dev: {s_rebound['std']:.6f}")
print(f"  Stability: {'PASSED' if s_rebound['mean'] > 0.1 else 'FAILED'}")

report = {
    "rebound_stress": {
        "mean_floor": s_rebound["mean"],
        "std_dev": s_rebound["std"],
        "steps": 10000,
        "K": 50.0
    }
}
with open(artifacts_dir / "rebound_stress_results.json", "w") as f:
    json.dump(report, f, indent=2)
