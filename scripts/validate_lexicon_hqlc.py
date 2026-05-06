import json
import subprocess
import sys
from pathlib import Path
import numpy as np

def main():
    out_dir = Path("results/2026-05-05_run08_lexicon_val_hqlc")
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Use fsa_rule_engine_sim_v1_cpp
    # Lexicon Term: HQLC
    # Role: computational_paradigm
    # Plan: Perform an 'up-down' sweep of forcing to measure hysteresis loop area.
    
    wrapper = Path("tools/fsa_rule_engine_sim_v1_cpp/sim_governed.py")
    
    # We'll do a simple two-stage simulation: 
    # Forcing up -> check state. Forcing down -> check state.
    
    results = []
    for eps in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0]:
        config = {
            "num_agents": 1024,
            "n_states": 5,
            "forbidden": 4, # Changed from [4]
            "res_thresh": 2, # Changed from 0.5
            "res_req": 1,   # Changed from 0.1
            "mismatch_rate": eps,
            "steps": 50
        }
        
        run_dir = data_dir / f"eps_{eps:.2f}_{len(results)}"
        run_dir.mkdir(parents=True, exist_ok=True)
        config_path = run_dir / "sim_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        setvars = r"C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
        cmd = f'call "{setvars}" >nul 2>&1 && "{sys.executable}" "{wrapper}" --config "{config_path}" --out "{run_dir}"'
        subprocess.run(cmd, shell=True, check=True)
        
        with open(run_dir / "summary.json", 'r') as f:
            summary = json.load(f)
            metrics = summary.get("final_metrics", {})
            results.append({"epsilon": eps, "active": metrics.get("active_count")})

    print("HQLC Hysteresis Sweep Results:")
    for r in results:
        print(f"epsilon={r['epsilon']}, active={r['active']}")
        
    with open(data_dir / "hysteresis_results.json", 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
