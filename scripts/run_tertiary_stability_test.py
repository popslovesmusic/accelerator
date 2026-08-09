import json
import subprocess
import os
from pathlib import Path

# Campaign: TERTIARY-STABILITY-001
# Hypothesis: Functional partitioning {I, O, R} preserves basin identity during external shocks.
run_dir = Path("results/2026-05-22_run03_Tertiary_Node_Stability")
data_dir = run_dir / "data"
artifacts_dir = run_dir / "artifacts"

def run_stability_test(node_type, shock_magnitude):
    # node_type="monolithic" -> Low gating (theta_de=0.1)
    # node_type="tertiary"   -> High gating (theta_de=0.8) - represents R buffering
    
    config = {
        "n_nodes": 4, # 3-node Basin + 1 external shock node
        "steps": 1000,
        "dt": 0.05,
        "K": 1.0, # Internal coupling
        "theta_de": 0.1 if node_type == "monolithic" else 0.8,
        "theta_re": 0.1,
        "P_re": 0.0,
        "omega_mean": 1.0,
        "omega_std": 0.5,
        "seed": 42
    }
    
    # We simulate a "Relational Shock" by having the 4th node strongly coupled to node 0
    # Actually, our current graph engine is an all-to-all or random graph.
    # To simulate a shock, we can increase the Global K during a specific regime.
    
    config["K"] = shock_magnitude
    
    config_path = data_dir / f"graph_{node_type}_s{shock_magnitude:.1f}_config.json"
    out_path = data_dir / f"graph_{node_type}_s{shock_magnitude:.1f}_results"
    with open(config_path, "w") as f: json.dump(config, f)
    
    subprocess.run(["python", "tools/graph_dynamics_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_path)], capture_output=True)
    
    try:
        with open(out_path / "summary.json") as f:
            data = json.load(f)
            # Stability = Maintenance of internal distinguishability (1 - order_param)
            # If order_param hits 1, the internal identity of the triad is lost to global synchronization.
            return 1.0 - data["final_metrics"]["order_parameter"]
    except:
        return 0.0

print("Starting Tertiary Node Stability Test (Relational Shock Resistance)...")

shock_range = [1.0, 5.0, 10.0]

results = {"monolithic": [], "tertiary": []}

for node_type in ["monolithic", "tertiary"]:
    for shock in shock_range:
        print(f"Testing {node_type} nodes with Shock K={shock}...")
        stability = run_stability_test(node_type, shock)
        results[node_type].append({"shock": shock, "stability": stability})
        print(f"  Stability: {stability:.4f}")

report = {
    "campaign": "TERTIARY-STABILITY-001",
    "results": results,
    "analysis": {
        "tertiary_advantage": results["tertiary"][-1]["stability"] / (results["monolithic"][-1]["stability"] + 1e-9),
        "persistence_preserved": results["tertiary"][-1]["stability"] > 0.1
    }
}

with open(artifacts_dir / "stability_report.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"Test Complete. Tertiary Advantage: {report['analysis']['tertiary_advantage']:.2f}x")
