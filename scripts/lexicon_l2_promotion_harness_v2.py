import json
import subprocess
import sys
import os
from pathlib import Path
import time

def run_command(cmd, description, env=None):
    print(f"Executing: {description}")
    # Inject oneAPI paths if possible
    curr_env = os.environ.copy()
    if env:
        curr_env.update(env)
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=curr_env)
    if result.returncode != 0:
        print(f"Error executing {description}:")
        print(result.stdout)
        print(result.stderr)
        return False
    return True

def main():
    timestamp = time.strftime("%Y-%m-%d_run%H%M%S")
    out_dir = Path(f"results/{timestamp}_lexicon_l2_promotion_v2")
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    report = {
        "timestamp": timestamp,
        "terms_tested": ["Relational Superposition", "HQLC"],
        "results": {}
    }

    # 1. Relational Superposition
    # Models: igsoa_complex_1d_cpp (Lattice), structural_box_sim_cpp (PDE)
    print("--- Testing Relational Superposition ---")
    superposition_results = {"lattice": None, "pde": None}
    
    # Lattice Run
    lat_config = {"num_nodes": 256, "steps": 100, "R_c": 5.0, "kappa": 0.1, "gamma": 0.1}
    lat_run_dir = data_dir / "superposition_lattice"
    lat_run_dir.mkdir(exist_ok=True)
    lat_config_path = lat_run_dir / "config.json"
    with open(lat_config_path, 'w') as f: json.dump(lat_config, f)
    
    if run_command([sys.executable, "tools/igsoa_complex_1d_cpp/sim_governed.py", "--config", str(lat_config_path), "--out", str(lat_run_dir)], "Superposition Lattice"):
        if (lat_run_dir / "metrics.json").exists():
            with open(lat_run_dir / "metrics.json", 'r') as f:
                superposition_results["lattice"] = json.load(f).get("psi_squared_mean")

    # PDE Run (Superposition mapped to high kappa variance)
    pde_config = {"num_nodes": 128, "kappa": 0.5, "s": 5.0, "steps": 200, "dt": 0.01}
    pde_run_dir = data_dir / "superposition_pde"
    pde_run_dir.mkdir(exist_ok=True)
    pde_config_path = pde_run_dir / "config.json"
    with open(pde_config_path, 'w') as f: json.dump(pde_config, f)
    
    if run_command([sys.executable, "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(pde_config_path), "--out", str(pde_run_dir)], "Superposition PDE"):
        with open(pde_run_dir / "summary.json", 'r') as f:
            superposition_results["pde"] = json.load(f)["final_metrics"].get("alignment_success_rate")

    report["results"]["Relational Superposition"] = superposition_results

    # 2. HQLC
    # Models: fsa_rule_engine_sim_v1_cpp (FSA), agent_based_sim_v1_cpp (Agent)
    print("--- Testing HQLC ---")
    hqlc_results = {"fsa": None, "agent": None}
    
    # Try to find oneAPI and inject to PATH
    oneapi_bin = r"C:\Program Files (x86)\Intel\oneAPI\compiler\latest\windows\bin"
    tbb_bin = r"C:\Program Files (x86)\Intel\oneAPI\tbb\latest\env\..\bin"
    env_override = {"PATH": f"{oneapi_bin};{tbb_bin};" + os.environ.get("PATH", "")}

    fsa_config = {"num_agents": 500, "n_states": 4, "steps": 100, "res_req": 2, "mismatch_rate": 0.1}
    fsa_run_dir = data_dir / "hqlc_fsa"
    fsa_run_dir.mkdir(exist_ok=True)
    fsa_config_path = fsa_run_dir / "config.json"
    with open(fsa_config_path, 'w') as f: json.dump(fsa_config, f)
    
    if run_command([sys.executable, "tools/fsa_rule_engine_sim_v1_cpp/sim_governed.py", "--config", str(fsa_config_path), "--out", str(fsa_run_dir)], "HQLC FSA", env=env_override):
        with open(fsa_run_dir / "summary.json", 'r') as f:
            hqlc_results["fsa"] = json.load(f)["final_metrics"].get("active_count")

    # Agent Run
    agent_config = {"agent_count": 1000, "steps": 100, "K_phi": 2.0, "kappa": 0.5, "mismatch_rate": 0.2}
    agent_run_dir = data_dir / "hqlc_agent"
    agent_run_dir.mkdir(exist_ok=True)
    agent_config_path = agent_run_dir / "config.json"
    with open(agent_config_path, 'w') as f: json.dump(agent_config, f)
    
    if run_command([sys.executable, "tools/agent_based_sim_v1_cpp/sim_governed.py", "--config", str(agent_config_path), "--out", str(agent_run_dir)], "HQLC Agent"):
        with open(agent_run_dir / "summary.json", 'r') as f:
            hqlc_results["agent"] = json.load(f)["final_metrics"].get("order_parameter")

    report["results"]["HQLC"] = hqlc_results

    with open(out_dir / "l2_promotion_report.json", 'w') as f:
        json.dump(report, f, indent=4)
    print(f"L2 Promotion Report saved to {out_dir / 'l2_promotion_report.json'}")

if __name__ == "__main__":
    main()
