import json
import subprocess
import sys
from pathlib import Path
import numpy as np

def main():
    out_dir = Path("results/2026-05-05_run09_lexicon_val_resolution_parameter")
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Use satp_higgs_1d_cpp
    # Lexicon Term: Resolution Parameter (B)
    # Role: transition_index
    # Plan: Sweep kappa to demonstrate the transition between regimes.
    
    wrapper = Path("tools/satp_higgs_1d_cpp/sim_governed.py")
    
    results = []
    for kappa in [0.01, 0.1, 1.0, 10.0]:
        config = {
            "num_nodes": 1024,
            "steps": 1000,
            "dt": 0.01,
            "kappa": kappa,
            "init_state": {
                "type": "phi_gaussian",
                "params": {
                    "amplitude": 1.0,
                    "sigma": 5.0
                }
            }
        }
        
        run_dir = data_dir / f"kappa_{kappa}"
        run_dir.mkdir(parents=True, exist_ok=True)
        config_path = run_dir / "sim_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        subprocess.run([sys.executable, str(wrapper), "--config", str(config_path), "--out", str(run_dir)], check=True)
        
        with open(run_dir / "metrics.json", 'r') as f:
            metrics = json.load(f)
            results.append({"kappa": kappa, "phi_rms": metrics.get("phi_rms")})

    print("Resolution Parameter Sweep Results:")
    for r in results:
        print(f"kappa={r['kappa']}, phi_rms={r['phi_rms']}")
        
    with open(data_dir / "regime_results.json", 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
