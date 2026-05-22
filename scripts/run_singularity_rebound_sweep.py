import json
import subprocess
import os
from pathlib import Path

# Campaign: SINGULARITY-REBOUND-001
# Hypothesis: Distinguishability Compression (K up) causes N=2 collapse but N=3 rebound/locking.
run_dir = Path("results/2026-05-22_run02_Singularity_Rebound")
data_dir = run_dir / "data"
artifacts_dir = run_dir / "artifacts"

def run_compression_sweep(n_nodes, k_values):
    sweep_results = []
    for k in k_values:
        config = {
            "n_nodes": n_nodes,
            "steps": 1000,
            "dt": 0.05,
            "K": k,
            "theta_de": 0.9,
            "theta_re": 0.1,
            "P_re": 0.0,
            "omega_mean": 1.0,
            "omega_std": 0.2, # Low diversity to force compression
            "seed": 42
        }
        
        config_path = data_dir / f"graph_n{n_nodes}_k{k:.1f}_config.json"
        out_path = data_dir / f"graph_n{n_nodes}_k{k:.1f}_results"
        with open(config_path, "w") as f: json.dump(config, f)
        
        subprocess.run(["python", "tools/graph_dynamics_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_path)], capture_output=True)
        
        try:
            with open(out_path / "summary.json") as f:
                data = json.load(f)
                order_param = data["final_metrics"]["order_parameter"]
                dist = 1.0 - order_param
                sweep_results.append({"K": k, "distinguishability": dist})
        except:
            sweep_results.append({"K": k, "distinguishability": 0.0})
            
    return sweep_results

print("Starting Singularity Rebound Sweep (Distinguishability Compression)...")

k_range = [1.0, 2.0, 5.0, 10.0, 20.0] # Increasing compression

n2_results = run_compression_sweep(2, k_range)
n3_results = run_compression_sweep(3, k_range)

report = {
    "campaign": "SINGULARITY-REBOUND-001",
    "n2_sweep": n2_results,
    "n3_sweep": n3_results,
    "analysis": {
        "n2_terminal_collapse": n2_results[-1]["distinguishability"] < 0.01,
        "n3_persistent_floor": n3_results[-1]["distinguishability"] > 0.1,
        "rebound_ratio": n3_results[-1]["distinguishability"] / (n2_results[-1]["distinguishability"] + 1e-9)
    }
}

with open(artifacts_dir / "rebound_report.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"Sweep Complete.")
print(f"N=2 Distinguishability at K=20: {n2_results[-1]['distinguishability']:.6f}")
print(f"N=3 Distinguishability at K=20: {n3_results[-1]['distinguishability']:.6f}")
print(f"Rebound Ratio: {report['analysis']['rebound_ratio']:.2f}")
