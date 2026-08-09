import json
import subprocess
import sys
import os
from pathlib import Path
import time

def run_command(cmd, description):
    print(f"Executing: {description}")
    # print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing {description}:")
        print(result.stdout)
        print(result.stderr)
        return False
    return True

def main():
    timestamp = time.strftime("%Y-%m-%d_run%H%M%S")
    out_dir = Path(f"results/{timestamp}_lexicon_l2_promotion")
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    report = {
        "timestamp": timestamp,
        "terms_tested": ["-(i)", "corridor", "Relational Superposition"],
        "results": {}
    }

    # 1. Orientation Selection -(i)
    print("--- Testing -(i) (Orientation Selection) ---")
    orientation_results = {"pde": None, "agent": None, "falsification": None}
    
    # Corrected param: 's' instead of 'epsilon_source'
    pde_config = {"num_nodes": 128, "kappa": 0.1, "s": 10.0, "steps": 200, "dt": 0.01}
    pde_run_dir = data_dir / "orientation_pde"
    pde_run_dir.mkdir(exist_ok=True)
    pde_config_path = pde_run_dir / "config.json"
    print(f"Config for Orientation PDE: {pde_config}")
    with open(pde_config_path, 'w') as f: json.dump(pde_config, f)
    
    if run_command([sys.executable, "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(pde_config_path), "--out", str(pde_run_dir)], "Orientation PDE"):
        with open(pde_run_dir / "summary.json", 'r') as f:
            orientation_results["pde"] = json.load(f)["final_metrics"].get("alignment_success_rate")

    agent_config = {"agent_count": 2000, "steps": 100, "K_phi": 2.0, "kappa": 0.5, "mismatch_rate": 0.05}
    agent_run_dir = data_dir / "orientation_agent"
    agent_run_dir.mkdir(exist_ok=True)
    agent_config_path = agent_run_dir / "config.json"
    with open(agent_config_path, 'w') as f: json.dump(agent_config, f)
    
    if run_command([sys.executable, "tools/agent_based_sim_v1_cpp/sim_governed.py", "--config", str(agent_config_path), "--out", str(agent_run_dir)], "Orientation Agent"):
        with open(agent_run_dir / "summary.json", 'r') as f:
            orientation_results["agent"] = json.load(f)["final_metrics"].get("order_parameter")

    # Falsification (Zero Forcing: s=0)
    pde_f_config = pde_config.copy()
    pde_f_config["s"] = 0.0
    pde_f_run_dir = data_dir / "orientation_falsification"
    pde_f_run_dir.mkdir(exist_ok=True)
    pde_f_config_path = pde_f_run_dir / "config.json"
    with open(pde_f_config_path, 'w') as f: json.dump(pde_f_config, f)
    
    if run_command([sys.executable, "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(pde_f_config_path), "--out", str(pde_f_run_dir)], "Orientation Falsification"):
        with open(pde_f_run_dir / "summary.json", 'r') as f:
            orientation_results["falsification"] = json.load(f)["final_metrics"].get("alignment_success_rate")

    report["results"]["-(i)"] = orientation_results

    # 2. Corridor
    print("--- Testing corridor (Topological Constraint) ---")
    corridor_results = {"pde": None, "ca": None}
    
    pde_c_config = {
        "grid_size": 64, "dt": 0.05, "steps": 200, 
        "D_diff": 0.1, "S_diff": 0.5, "beta": 2.0, "growth_thresh": 0.2,
        "domain_decay": 0.01, "signal_decay": 0.05, "source_pos": [32, 32],
        "source_radius": 2, "source_strength": 5.0
    }
    pde_c_run_dir = data_dir / "corridor_pde"
    pde_c_run_dir.mkdir(exist_ok=True)
    pde_c_config_path = pde_c_run_dir / "config.json"
    print(f"Config for Corridor PDE: {pde_c_config}")
    with open(pde_c_config_path, 'w') as f: json.dump(pde_c_config, f)
    
    if run_command([sys.executable, "tools/rd_moving_boundary_sim_v1/sim.py", "--config", str(pde_c_config_path), "--out", str(pde_c_run_dir)], "Corridor PDE"):
        with open(pde_c_run_dir / "summary.json", 'r') as f:
            corridor_results["pde"] = json.load(f)["final_metrics"].get("active_area")

    ca_config = {"width": 64, "height": 64, "steps": 100, "D": 0.1, "source_strength": 5.0, "source_radius": 3}
    ca_run_dir = data_dir / "corridor_ca"
    ca_run_dir.mkdir(exist_ok=True)
    ca_config_path = ca_run_dir / "config.json"
    with open(ca_config_path, 'w') as f: json.dump(ca_config, f)
    
    if run_command([sys.executable, "tools/ca_admissibility_sim_v1_cpp/sim_governed.py", "--config", str(ca_config_path), "--out", str(ca_run_dir)], "Corridor CA"):
        with open(ca_run_dir / "summary.json", 'r') as f:
            corridor_results["ca"] = json.load(f)["final_metrics"].get("active_fraction")

    report["results"]["corridor"] = corridor_results

    # 3. Relational Superposition
    print("--- Testing Relational Superposition ---")
    superposition_results = {"lattice": None}
    lat_config = {"num_nodes": 256, "steps": 100, "R_c": 5.0, "kappa": 0.1, "gamma": 0.1}
    lat_run_dir = data_dir / "superposition_lattice"
    lat_run_dir.mkdir(exist_ok=True)
    lat_config_path = lat_run_dir / "config.json"
    with open(lat_config_path, 'w') as f: json.dump(lat_config, f)
    
    if run_command([sys.executable, "tools/igsoa_complex_1d_cpp/sim_governed.py", "--config", str(lat_config_path), "--out", str(lat_run_dir)], "Superposition Lattice"):
        if (lat_run_dir / "metrics.json").exists():
            with open(lat_run_dir / "metrics.json", 'r') as f:
                superposition_results["lattice"] = json.load(f).get("psi_squared_mean")

    report["results"]["Relational Superposition"] = superposition_results

    with open(out_dir / "l2_promotion_report.json", 'w') as f:
        json.dump(report, f, indent=4)
    print(f"L2 Promotion Report saved to {out_dir / 'l2_promotion_report.json'}")

if __name__ == "__main__":
    main()
