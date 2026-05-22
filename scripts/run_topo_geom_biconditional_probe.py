import json
import subprocess
import os
from pathlib import Path

# Campaign: TOPOLOGY-GEOMETRY-001
# Goal: Prove that Topology (connectivity) and Geometry (accessibility) are biconditional.
run_dir = Path("results/2026-05-22_run04_Topology_Geometry_Biconditional")
data_dir = run_dir / "data"
artifacts_dir = run_dir / "artifacts"

def run_probe(label, k, p_re, theta_re):
    config = {
        "n_nodes": 32,
        "steps": 2000,
        "dt": 0.05,
        "K": k,
        "theta_de": 0.5,
        "theta_re": theta_re,
        "P_re": p_re,
        "omega_mean": 1.0,
        "omega_std": 0.5, # More diversity
        "seed": 42
    }
    
    config_path = data_dir / f"config_{label}.json"
    out_path = data_dir / f"results_{label}"
    with open(config_path, "w") as f: json.dump(config, f)
    
    subprocess.run(["python", "tools/graph_dynamics_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_path)], capture_output=True)
    
    try:
        with open(out_path / "summary.json") as f:
            data = json.load(f)
            return {
                "degree": data["final_metrics"].get("avg_degree", 0),
                "op": data["final_metrics"].get("order_parameter", 0),
                "edges": data["final_metrics"].get("edge_count", 0)
            }
    except: return {}

print("Starting Topology-Geometry Biconditional Probe...")

# Test 1: Topology deforms Geometry (High Rewiring based on Residue)
print("Test 1: Topological Deformation...")
t_deform = run_probe("topo_deform", k=2.5, p_re=0.8, theta_re=0.1)

# Test 2: Geometric Constraint (Restricted Rewiring/Accessibility)
print("Test 2: Geometric Constraint...")
g_constraint = run_probe("geom_constraint", k=2.5, p_re=0.01, theta_re=0.9)

report = {
    "campaign": "TOPOLOGY-GEOMETRY-001",
    "topo_deform_results": t_deform,
    "geom_constraint_results": g_constraint,
    "analysis": {
        "connectivity_gain": t_deform["degree"] / (g_constraint["degree"] + 1e-9),
        "coherence_locking": t_deform["op"] / (g_constraint["op"] + 1e-9)
    },
    "status": "completed"
}

with open(artifacts_dir / "biconditional_report.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"Probe Complete.")
print(f"Topological Deformation Degree: {t_deform.get('degree', 0):.4f}")
print(f"Geometric Constraint Degree: {g_constraint.get('degree', 0):.4f}")
print(f"Biconditional Gain (Connectivity): {report['analysis']['connectivity_gain']:.2f}x")
