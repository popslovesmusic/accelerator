
import os
import json
import subprocess
from pathlib import Path

def run_sweep():
    base_config_path = "configs/validation/structural_box_sim_cpp/base_flat.json"
    with open(base_config_path, "r") as f:
        base_config = json.load(f)
    
    sweep_dir = "outputs/runs/h1_threshold_sweep"
    os.makedirs(sweep_dir, exist_ok=True)
    
    results = []
    
    s_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    for s in s_values:
        config = base_config.copy()
        config["s"] = s
        config_path = os.path.join(sweep_dir, f"config_s_{s}.json")
        out_dir = os.path.join(sweep_dir, f"run_s_{s}")
        
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
            
        print(f"Running simulation with s={s}...")
        cmd = f"python tools/structural_box_sim_cpp/sim_governed.py --config {config_path} --out {out_dir}"
        subprocess.run(cmd, shell=True, check=True)
        
        # Collect results
        metrics_path = os.path.join(out_dir, "metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
            results.append({
                "s": s,
                "alignment_success_rate": metrics.get("alignment_success_rate"),
                "epsilon_max": metrics.get("epsilon_max"),
                "epsilon_active_fraction": metrics.get("epsilon_active_fraction")
            })
            
    with open(os.path.join(sweep_dir, "sweep_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Sweep completed. Results saved to {sweep_dir}/sweep_results.json")

if __name__ == "__main__":
    run_sweep()
