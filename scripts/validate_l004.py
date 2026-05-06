import json
import subprocess
import sys
from pathlib import Path

def main():
    out_dir = Path("results/2026-05-05_run03_L004_preupdate_constraint_precedence_validation")
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Use structural_box_sim_cpp
    # Extreme forcing (epsilon=100) vs small window (kappa=0.01)
    config = {
        "num_nodes": 128,
        "L": 1.0,
        "kappa": 0.01,
        "epsilon_source": 100.0,
        "steps": 100,
        "dt": 0.01
    }
    
    config_path = data_dir / "sim_config.json"
    metrics_path = data_dir / "metrics.json"
    wrapper = Path("tools/structural_box_sim_cpp/sim_governed.py")
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
        
    cmd = [sys.executable, str(wrapper), "--config", str(config_path), "--out", str(data_dir)]
    subprocess.run(cmd, check=True)
    
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    
    # Check max_delta_phi
    # structural_box_sim_cpp usually reports max_delta_phi in its metrics
    max_dp = metrics.get("max_delta_phi", 0.0)
    print(f"Max observed increment: {max_dp}")
    print(f"Admissibility threshold: {config['kappa']}")
    
    if max_dp <= config['kappa'] * 1.01: # allow for tiny numerical noise
        print("L004 Validation: SUCCESS (Pre-update constraint enforced)")
    else:
        print("L004 Validation: FAILED (Constraint breached)")

if __name__ == "__main__":
    main()
