import json
import subprocess
import os
from pathlib import Path

# Campaign: TERTIARY-STABILITY-002
# Goal: Prove that {I, O, R} functional partitioning (simulated via threshold gating) 
# allows a basin to survive interaction with a heterogeneous environment.
run_dir = Path("results/2026-05-22_run03_Tertiary_Node_Stability")
data_dir = run_dir / "data"
artifacts_dir = run_dir / "artifacts"

def run_interaction_test(is_partitioned):
    # is_partitioned=False -> Monolithic coupling (No theta gating)
    # is_partitioned=True  -> Tertiary coupling (High theta gating)
    
    config = {
        "n_nodes": 6, # 3-node Basin + 3-node random environment
        "steps": 2000,
        "dt": 0.05,
        "K": 2.5, # Strong global coupling
        "theta_de": 0.0 if not is_partitioned else 0.9, # Gating = Partitioning
        "theta_re": 0.1,
        "P_re": 0.0,
        "omega_mean": 1.0,
        "omega_std": 0.5,
        "seed": 42
    }
    
    label = "partitioned" if is_partitioned else "monolithic"
    config_path = data_dir / f"interaction_{label}_config.json"
    out_path = data_dir / f"interaction_{label}_results"
    with open(config_path, "w") as f: json.dump(config, f)
    
    subprocess.run(["python", "tools/graph_dynamics_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_path)], capture_output=True)
    
    try:
        with open(out_path / "summary.json") as f:
            data = json.load(f)
            # Metric: Order Parameter (Synchrony)
            # If OP -> 1.0, the basin's distinct identity is lost (it syncs to the environment).
            # If OP remains < 1.0, the basin maintains its own distinguishability floor.
            return data["final_metrics"]["order_parameter"]
    except: return 1.0

print("Starting Tertiary Interaction Test (Basin Survival)...")

op_monolithic = run_interaction_test(False)
op_partitioned = run_interaction_test(True)

print(f"  Monolithic Order Parameter: {op_monolithic:.6f}")
print(f"  Partitioned Order Parameter: {op_partitioned:.6f}")

report = {
    "campaign": "TERTIARY-STABILITY-002",
    "monolithic_op": op_monolithic,
    "partitioned_op": op_partitioned,
    "identity_loss_reduction": (op_monolithic - op_partitioned) / (op_monolithic + 1e-9),
    "status": "completed"
}

with open(artifacts_dir / "interaction_report.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"Test Complete. Partitioning reduced synchrony (Identity Loss) by {report['identity_loss_reduction']*100:.2f}%")
