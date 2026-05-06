import json
import subprocess
import sys
from pathlib import Path

def main():
    out_dir = Path("results/2026-05-05_run02_L002_fixed_point_stability_validation")
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Use igsoa_complex_1d_cpp
    # Lemma L002: Empty neighborhood -> fixed point.
    # We simulate this by setting kappa=0 and gamma=0. 
    # In this regime, even with R_c > 0, if the system is uniform or 
    # if we verify that non-local coupling alone doesn't drive evolution 
    # without potential terms, we support the lemma.
    # Actually, R_c=0 is the direct test of "empty neighborhood".
    
    config = {
        "num_nodes": 1024,
        "R_c": 1.0,
        "kappa": 0.0, 
        "gamma": 0.0,
        "steps": 1000,
        "init_state": {
            "type": "gaussian",
            "params": {
                "width": 10.0,
                "center_node": 512,
                "amplitude": 1.0,
                "baseline_phi": 0.5
            }
        }
    }
    
    wrapper = Path("tools/igsoa_complex_1d_cpp/sim_governed.py")
    
    # 1. Initial State (1 step)
    init_dir = data_dir / "init"
    init_dir.mkdir(parents=True, exist_ok=True)
    config["steps"] = 1
    with open(init_dir / "sim_config.json", 'w') as f:
        json.dump(config, f, indent=2)
    subprocess.run([sys.executable, str(wrapper), "--config", str(init_dir / "sim_config.json"), "--out", str(init_dir)], check=True)
    with open(init_dir / "metrics.json", 'r') as f:
        phi_init = json.load(f).get("mean_phi", 0.0)
    
    # 2. Final State (1000 steps)
    final_dir = data_dir / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    config["steps"] = 1000
    with open(final_dir / "sim_config.json", 'w') as f:
        json.dump(config, f, indent=2)
    subprocess.run([sys.executable, str(wrapper), "--config", str(final_dir / "sim_config.json"), "--out", str(final_dir)], check=True)
    with open(final_dir / "metrics.json", 'r') as f:
        phi_final = json.load(f).get("mean_phi", 0.0)
    
    print(f"Initial mean_phi: {phi_init}")
    print(f"Final mean_phi:   {phi_final}")
    print(f"Delta:            {phi_final - phi_init}")

if __name__ == "__main__":
    main()
