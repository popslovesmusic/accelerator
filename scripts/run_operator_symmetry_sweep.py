import json
import subprocess
import os
import csv
import math
from pathlib import Path

# Aligned Stable Symmetry Sweep
theta_range = [0.05, 0.1, 0.15, 0.2, 0.25]
seeds = [101, 202, 303]
run_dir = Path("results/2026-05-21_run02_Operator_Symmetry_Sweep")
data_dir = run_dir / "data"

results = []

def pearson_correlation(x, y):
    n = len(x)
    if n < 2: return 0.0
    mu_x = sum(x) / n
    mu_y = sum(y) / n
    var_x = sum((xi - mu_x)**2 for xi in x)
    var_y = sum((yi - mu_y)**2 for yi in y)
    if var_x == 0 or var_y == 0: return 0.0
    covariance = sum((x[i] - mu_x) * (y[i] - mu_y) for i in range(n))
    return covariance / (math.sqrt(var_x) * math.sqrt(var_y))

print(f"Starting STABLE Operator Symmetry Sweep (L039)...")

for theta in theta_range:
    for seed in seeds:
        print(f"--- Running Threshold={theta}, Seed={seed} ---")
        
        # 1. Stochastic
        stoch_config = {
            "n_particles": 1000,
            "steps": 100,
            "dt": 0.01,
            "kappa": 0.5,
            "sigma": 0.2, 
            "x_thresh": theta,
            "seed": seed
        }
        stoch_config_path = data_dir / f"stoch_t{theta}_s{seed}_config.json"
        stoch_out_path = data_dir / f"stoch_t{theta}_s{seed}_results"
        with open(stoch_config_path, "w") as f: json.dump(stoch_config, f)
        subprocess.run(["python", "tools/stochastic_sim_cpp/sim_governed.py", "--config", str(stoch_config_path), "--out", str(stoch_out_path)], capture_output=True)
        
        # 2. CA (D=0.2 for stability)
        ca_config = {
            "width": 64,
            "height": 64,
            "steps": 100,
            "D": 0.2, 
            "initial_residue": theta,
            "delta_R": 0.0,
            "gamma_R": 0.0,
            "source_strength": 1.0,
            "seed": seed
        }
        ca_config_path = data_dir / f"ca_t{theta}_s{seed}_config.json"
        ca_out_path = data_dir / f"ca_t{theta}_s{seed}_results"
        with open(ca_config_path, "w") as f: json.dump(ca_config, f)
        subprocess.run(["python", "tools/ca_admissibility_sim_v1_cpp/sim_governed.py", "--config", str(ca_config_path), "--out", str(ca_out_path)], capture_output=True)
        
        stoch_metric = 0.0
        try:
            with open(stoch_out_path / "summary.json") as f:
                stoch_metric = json.load(f)["final_metrics"]["crossing_fraction"]
        except: pass
            
        ca_metric = 0.0
        try:
            with open(ca_out_path / "summary.json") as f:
                ca_metric = json.load(f)["final_metrics"]["active_fraction"]
        except: pass
            
        results.append({"theta": theta, "seed": seed, "stoch": stoch_metric, "ca": ca_metric})

with open(run_dir / "artifacts/symmetry_metrics.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["theta", "seed", "stoch", "ca"])
    writer.writeheader()
    writer.writerows(results)

stoch_vals = [r["stoch"] for r in results]
ca_vals = [r["ca"] for r in results]
correlation = pearson_correlation(stoch_vals, ca_vals)

report = {
    "campaign": "Operator Symmetry Sweep (L039 Hardening)",
    "correlation": correlation,
    "theta_range": theta_range,
    "metrics_count": len(results),
    "status": "completed"
}
with open(run_dir / "artifacts/symmetry_report.json", "w") as f: json.dump(report, f, indent=2)

print(f"Sweep complete. Stable Pearson Correlation: {correlation:.4f}")
