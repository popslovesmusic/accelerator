import json
import subprocess
import os
from pathlib import Path

# Campaign: FALSIFICATION-STRESS-001
# Objective: Adversarial testing of core laws.

run_dir = Path("results/2026-05-22_run05_Falsification_Attack_Suite")
data_dir = run_dir / "data"
artifacts_dir = run_dir / "artifacts"

def run_attack(name, config_mod):
    config = {
        "n_nodes": 12,
        "steps": 2000,
        "dt": 0.05,
        "K": 2.0,
        "theta_de": 0.5,
        "theta_re": 0.1,
        "P_re": 0.0,
        "omega_mean": 1.0,
        "omega_std": 0.2,
        "seed": 42
    }
    config.update(config_mod)
    
    config_path = data_dir / f"config_{name}.json"
    out_path = data_dir / f"results_{name}"
    with open(config_path, "w") as f: json.dump(config, f)
    
    subprocess.run(["python", "tools/graph_dynamics_sim_v1_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_path)], capture_output=True)
    
    try:
        with open(out_path / "summary.json") as f:
            return json.load(f)
    except: return {}

results = {}

# --- Attack A: The Binary Lock Attack (Target: T001) ---
# Attempt to stabilize N=2 using extreme omega diversity and high K.
print("Executing Attack A: Binary Lock...")
results["binary_lock"] = run_attack("binary_lock", {
    "n_nodes": 2,
    "K": 10.0, 
    "omega_std": 5.0 # Extreme diversity to prevent sync
})

# --- Attack B: The Symmetrical Death Attack (Target: SING-001) ---
# Attempt to kill rebound by forcing omega diversity to zero.
print("Executing Attack B: Symmetrical Death...")
results["symmetrical_death"] = run_attack("symmetrical_death", {
    "n_nodes": 3,
    "K": 20.0,
    "omega_std": 0.0 # Absolute Global Symmetry
})

# --- Attack C: Monolithic Persistence Attack (Target: L043) ---
# Attempt to stabilize a monolithic node under high-K shock.
print("Executing Attack C: Monolithic Persistence...")
results["monolithic_persistence"] = run_attack("monolithic_persistence", {
    "n_nodes": 6,
    "K": 15.0,
    "theta_de": 0.0, # Zero gating (monolithic)
    "omega_std": 0.5
})

# --- Attack D: Ghost Geometry Attack (Target: L045) ---
# Attempt to find geometric signal (OP) without topological residue (edges).
print("Executing Attack D: Ghost Geometry...")
results["ghost_geometry"] = run_attack("ghost_geometry", {
    "n_nodes": 12,
    "K": 0.0, # Zero coupling (No edges)
    "omega_std": 0.5
})

# --- Analysis ---
analysis = {
    "attack_a_success": results["binary_lock"]["final_metrics"]["order_parameter"] < 0.9, # If OP low, it didn't collapse
    "attack_b_success": results["symmetrical_death"]["final_metrics"]["order_parameter"] > 0.999, # If OP ~1, rebound failed
    "attack_c_success": results["monolithic_persistence"]["final_metrics"]["order_parameter"] > 0.9, # If OP high, identity lost (Expected)
    "attack_d_success": results["ghost_geometry"]["final_metrics"]["order_parameter"] > 0.1 # If OP high without edges, ghost signal found
}

report = {
    "campaign": "FALSIFICATION-STRESS-001",
    "results": results,
    "analysis": analysis,
    "status": "completed"
}

with open(artifacts_dir / "falsification_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("Attack Suite Complete.")
for attack, success in analysis.items():
    print(f"  {attack}: {success}")
