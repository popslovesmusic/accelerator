import json
import subprocess
import sys
from pathlib import Path
import numpy as np

def main():
    out_dir = Path("results/2026-05-05_run06_lexicon_val_relational_superposition")
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Use igsoa_complex_1d_cpp
    # Lexicon Term: Relational Superposition
    # Role: computational_primitive
    # Plan: Demonstrate non-local interference between multiple Gaussian wave packets.
    
    config = {
        "num_nodes": 1024,
        "R_c": 10.0,
        "kappa": 0.1,
        "gamma": 0.0,
        "steps": 500,
        "init_state": {
            "type": "gaussian",
            "params": {
                "width": 10.0,
                "center_node": 512,
                "amplitude": 1.0,
                "baseline_phi": 0.0
            }
        }
    }
    
    wrapper = Path("tools/igsoa_complex_1d_cpp/sim_governed.py")
    config_path = data_dir / "sim_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
        
    subprocess.run([sys.executable, str(wrapper), "--config", str(config_path), "--out", str(data_dir)], check=True)
    
    with open(data_dir / "metrics.json", 'r') as f:
        metrics = json.load(f)
    
    # Interference Contrast (IC) proxy: variance of psi_squared across grid.
    # In superposition, wave packets spread and interfere.
    print(f"Final psi_squared_mean: {metrics.get('psi_squared_mean')}")
    
if __name__ == "__main__":
    main()
