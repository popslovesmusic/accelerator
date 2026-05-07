import os
import json
import subprocess
import numpy as np
from pathlib import Path

def run_lattice_batch(run_dir):
    tools_dir = Path("tools")
    sim_script = tools_dir / "igsoa_complex_2d_cpp" / "sim_governed.py"
    data_dir = run_dir / "data"
    
    scenarios = ["asymmetric", "symmetric", "control"]
    
    for scenario in scenarios:
        print(f"Running Lattice Scenario: {scenario}")
        config_path = data_dir / f"config_{scenario}.json"
        out_dir = run_dir / f"lattice_{scenario}"
        subprocess.run([
            "python", str(sim_script),
            "--config", str(config_path),
            "--out", str(out_dir)
        ], check=True)
        
        state_path = out_dir / "state_final.json"
        if state_path.exists():
            with open(state_path, 'r') as f:
                state = json.load(f)
                if "grid" in state:
                    grid_data = np.array(state["grid"])
                else:
                    nx, ny = 64, 64
                    grid_data = np.array(state).reshape((nx, ny))
                
                intensity = np.abs(grid_data)
                np.savetxt(out_dir / "grid_intensity.csv", intensity, delimiter=",")
                
                print(f"Running TDA on {scenario}")
                tda_config = out_dir / "tda_config.json"
                with open(tda_config, 'w') as tf:
                    json.dump({
                        "mode": "spatial",
                        "grid_csv": str((out_dir / "grid_intensity.csv").absolute()),
                        "threshold": 0.1
                    }, tf)
                
                tda_script = tools_dir / "tda_module_v2_cpp" / "sim_governed.py"
                subprocess.run([
                    "python", str(tda_script),
                    "--config", str(tda_config),
                    "--out", str(out_dir / "tda")
                ], check=True)

def run_abm_batch(run_dir):
    tools_dir = Path("tools")
    sim_script = tools_dir / "agent_based_sim_v1_cpp" / "sim_governed.py"
    data_dir = run_dir / "data"
    
    scenarios = ["asymmetric", "symmetric"]
    
    for scenario in scenarios:
        print(f"Running ABM Scenario: {scenario}")
        config_path = data_dir / f"config_abm_{scenario}.json"
        out_dir = run_dir / f"abm_{scenario}"
        subprocess.run([
            "python", str(sim_script),
            "--config", str(config_path),
            "--out", str(out_dir)
        ], check=True)

def main():
    run_dir = Path("results/2026-05-06_run01_relational_alignment_validation")
    run_lattice_batch(run_dir)
    run_abm_batch(run_dir)
    
if __name__ == "__main__":
    main()
