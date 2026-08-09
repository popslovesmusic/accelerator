import json
import subprocess
import os
import statistics
from pathlib import Path

# LOCAL-STRESS-001 - Phase 1 (CA): 3-Peak Multi-Model Audit
# Rigor: 50 seeds, CA mechanism.

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

def run_ca_seed(reach_d, seed):
    config = {
        "width": 64,
        "height": 64,
        "steps": 1000,
        "D": reach_d,
        "initial_residue": 0.2,
        "delta_R": 0.1,
        "gamma_R": 0.05,
        "source_strength": 1.0,
        "seed": seed
    }
    
    label = f"ca_r{reach_d:.2f}_s{seed}"
    config_path = data_dir / f"{label}_config.json"
    out_path = data_dir / f"{label}_results"
    with open(config_path, "w") as f: json.dump(config, f)
    
    subprocess.run(["python", "tools/ca_admissibility_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_path)], capture_output=True)
    
    try:
        with open(out_path / "summary.json") as f:
            data = json.load(f)
            # Active Fraction = Measure of persistence.
            return data["final_metrics"]["active_fraction"]
    except: return 0.0

n_seeds = 50
print(f"Starting CA 3-Peak Audit ({n_seeds} seeds)...")

# D=0.05 -> Binary-like (nearest neighbors only)
# D=0.25 -> Triadic-like (loop closure possible)
r_low = 0.05
r_high = 0.25

low_vals = [run_ca_seed(r_low, s) for s in range(n_seeds)]
high_vals = [run_ca_seed(r_high, s) for s in range(n_seeds)]

s_low = get_stats(low_vals)
s_high = get_stats(high_vals)
jump = s_high["mean"] / (s_low["mean"] + 1e-9)

print(f"CA Audit Complete.")
print(f"  Restricted (D={r_low}): Mean Persistence = {s_low['mean']:.4f}")
print(f"  Open (D={r_high}): Mean Persistence = {s_high['mean']:.4f}")
print(f"  Persistence Jump: {jump:.2f}x")

report = {
    "ca_audit": {
        "low": s_low,
        "high": s_high,
        "jump": jump
    }
}
with open(artifacts_dir / "ca_audit_results.json", "w") as f:
    json.dump(report, f, indent=2)
