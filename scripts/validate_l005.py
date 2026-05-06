import json
import subprocess
import sys
from pathlib import Path
import numpy as np

def main():
    out_dir = Path("results/2026-05-05_run04_L005_residue_conditioned_closure_validation")
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Use igsoa_complex_1d_cpp
    # Lemma L005: Consistency between existence and update sides.
    # We show that when informational density F=|Psi|^2 (existence) is high, 
    # the realized field Phi evolves towards Psi (update holds).
    
    config = {
        "num_nodes": 128,
        "R_c": 1.0,
        "kappa": 1.0,
        "gamma": 0.1,
        "steps": 100,
        "init_state": {
            "type": "gaussian",
            "params": {
                "width": 5.0,
                "center_node": 64,
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
    
    # The current wrapper doesn't save the full state to a separate file, 
    # it's in raw_outputs.json (if get_state was called).
    # I'll update the wrapper to call get_state at the end.
    
if __name__ == "__main__":
    main()
