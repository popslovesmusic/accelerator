
import os
import json
from pathlib import Path

def collect_results():
    sweep_dir = "outputs/runs/h1_threshold_sweep"
    results = []
    
    s_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    for s in s_values:
        out_dir = os.path.join(sweep_dir, f"run_s_{s}")
        summary_path = os.path.join(out_dir, "summary.json")
        
        if os.path.exists(summary_path):
            with open(summary_path, "r") as f:
                summary = json.load(f)
            
            final_metrics = summary.get("final_metrics", {})
            report = summary.get("report", {})
            
            results.append({
                "s": s,
                "alignment_success_rate": report.get("alignment_success_rate"),
                "epsilon_max": final_metrics.get("epsilon_max"),
                "epsilon_active_fraction": final_metrics.get("epsilon_active_fraction"),
                "residue_max": final_metrics.get("residue_max")
            })
            
    with open(os.path.join(sweep_dir, "sweep_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results collected and saved to {sweep_dir}/sweep_results.json")

if __name__ == "__main__":
    collect_results()
