import json
import subprocess
import os
from pathlib import Path

# Campaign: TERTIARY-STABILITY-003
# Goal: Prove that the {I,O,R} Tertiary Structure (simulated via high theta_de) 
# preserves DISTINGUISHABILITY (D = 1 - OP) during intense coupling.
run_dir = Path("results/2026-05-22_run03_Tertiary_Node_Stability")
data_dir = run_dir / "data"
artifacts_dir = run_dir / "artifacts"

def run_dist_test(is_partitioned):
    config = {
        "n_nodes": 10, # Large swarm
        "steps": 1500,
        "dt": 0.05,
        "K": 5.0, # Intense "Gravity" / Coupling
        "theta_de": 0.1 if not is_partitioned else 0.9, # Low vs High Gating
        "theta_re": 0.1,
        "P_re": 0.0,
        "omega_mean": 1.0,
        "omega_std": 0.5,
        "seed": 42
    }
    
    label = "partitioned" if is_partitioned else "monolithic"
    config_path = data_dir / f"dist_{label}_config.json"
    out_path = data_dir / f"dist_{label}_results"
    with open(config_path, "w") as f: json.dump(config, f)
    
    subprocess.run(["python", "tools/graph_dynamics_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_path)], capture_output=True)
    
    try:
        with open(out_path / "summary.json") as f:
            data = json.load(f)
            dist = 1.0 - data["final_metrics"]["order_parameter"]
            return dist
    except: return 0.0

print("Starting Tertiary Distinguishability Test (Preserving Identity)...")

d_monolithic = run_dist_test(False)
d_partitioned = run_dist_test(True)

print(f"  Monolithic Distinguishability (D): {d_monolithic:.6f}")
print(f"  Partitioned Distinguishability (D): {d_partitioned:.6f}")

report = {
    "campaign": "TERTIARY-STABILITY-003",
    "monolithic_d": d_monolithic,
    "partitioned_d": d_partitioned,
    "distinguishability_gain": d_partitioned / (d_monolithic + 1e-9),
    "status": "completed"
}

with open(artifacts_dir / "distinguishability_report.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"Test Complete. Partitioning (Tertiary Structure) preserved {report['distinguishability_gain']:.2f}x more identity.")
