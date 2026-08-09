import json
import subprocess
import os
import statistics
from pathlib import Path

# LOCAL-STRESS-001 - Phase 1: 3-Peak Multi-Model Audit
# Rigor: 20 seeds per K, 2 model classes.

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

def run_graph_seed(n_nodes, seed, k_val):
    config = {
        "n_nodes": n_nodes,
        "steps": 2000,
        "dt": 0.05,
        "K": k_val,
        "theta_de": 1.0, # Never decouple
        "theta_re": 1.0, # Always recouple
        "P_re": 1.0,     # Force connection
        "omega_mean": 1.0,
        "omega_std": 0.5,
        "seed": seed
    }
    
    label = f"graph_n{n_nodes}_s{seed}_k{k_val:.1f}"
    config_path = data_dir / f"{label}_config.json"
    out_path = data_dir / f"{label}_results"
    with open(config_path, "w") as f: json.dump(config, f)
    
    subprocess.run(["python", "tools/graph_dynamics_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_path)], capture_output=True)
    
    try:
        with open(out_path / "summary.json") as f:
            data = json.load(f)
            # D = 1 - OP. 
            # If N=2 collapses, OP -> 1.0, D -> 0.
            # If N=3 locks, OP < 1.0, D > 0.
            return 1.0 - data["final_metrics"]["order_parameter"]
    except: return 0.0

k_range = [1.0, 2.5, 5.0, 10.0]
n_seeds = 20
print(f"Starting 3-Peak K-Sweep Audit ({n_seeds} seeds)...")

sweep_results = []

for k in k_range:
    print(f"Testing K={k}...")
    n2_vals = [run_graph_seed(2, s, k) for s in range(n_seeds)]
    n3_vals = [run_graph_seed(3, s, k) for s in range(n_seeds)]
    s2 = get_stats(n2_vals)
    s3 = get_stats(n3_vals)
    jump = s3["mean"] / (s2["mean"] + 1e-9)
    sweep_results.append({
        "K": k,
        "n2": s2,
        "n3": s3,
        "jump": jump
    })
    print(f"  K={k:.1f}: N2_D={s2['mean']:.4f}, N3_D={s3['mean']:.4f}, Jump={jump:.2f}x")

report = {
    "campaign": "LOCAL-STRESS-001-P1",
    "k_sweep": sweep_results,
    "status": "completed"
}

with open(artifacts_dir / "audit_results.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"Audit Complete. Results saved to {artifacts_dir / 'audit_results.json'}")
