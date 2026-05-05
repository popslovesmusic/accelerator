import os
import json
import subprocess
import pandas as pd
import numpy as np
import datetime
from pathlib import Path

# Metadata
RUN_ID = "research_quantum_falsification_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
LOGS_DIR = OUTPUT_ROOT / "logs"
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_falsification():
    # FV-3: kappa=0 (No persistence residue)
    # Testing if interference still occurs without topological memory
    s = 0.12
    spacings = [0.0, 0.4]
    seeds = [42, 43, 44]
    
    results = []
    
    base_config = {
        "nx": 512,
        "dt": 1e-4,
        "length": 1.0,
        "D_epsilon": 6e-4,
        "D_rho": 4e-4,
        "D_R": 2e-4,
        "a": 0.6, "b": 1.2, "c": 2.0,
        "alpha": 0.7, "beta": 0.8, "gamma": 1.2,
        "u": 0.15, "v": 0.08,
        "kappa": 0.0, # NO PERSISTENCE
        "lambda_R": 0.8, "h": 0.08,
        "steps": 4000,
        "s_duration": 2000,
        "activity_thresh": 0.05
    }

    for d in spacings:
        for seed in seeds:
            job_id = f"pde_fv3_d_{d}_seed_{seed}"
            out_dir = JOBS_DIR / job_id
            os.makedirs(out_dir, exist_ok=True)
            
            config = base_config.copy()
            config["s"] = s
            config["initial_condition"] = {"epsilon_kind": "gaussian", "amplitude": 0.4, "sigma": 0.05, "offset": d, "seed": seed}
            
            with open(out_dir / "config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            print(f"[{datetime.datetime.now()}] [FV-3] Running d={d}, seed={seed}")
            cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(out_dir / "config.json"), "--out", str(out_dir)]
            subprocess.run(cmd, capture_output=True)
            
            summary_path = out_dir / "summary.json"
            if summary_path.exists():
                with open(summary_path, "r") as f:
                    summary = json.load(f)
                results.append({
                    "vector": "FV-3",
                    "spacing_d": d,
                    "seed": seed,
                    "alignment_success_rate": summary["final_metrics"]["alignment_success_rate"]
                })

    return results

def main():
    print(f"Starting Quantum Falsification Research: {RUN_ID}")
    results = run_falsification()
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_ROOT / "falsification_results.csv", index=False)
    
    summary = df.groupby("spacing_d")["alignment_success_rate"].mean()
    contrast = summary.get(0.0, 0) - summary.get(0.4, 0)
    print(f"Falsification Contrast (kappa=0): {contrast}")
    
    manifest = {
        "run_id": RUN_ID,
        "timestamp": datetime.datetime.now().isoformat(),
        "total_runs": len(results),
        "falsification_contrast": float(contrast),
        "status": "completed"
    }
    with open(OUTPUT_ROOT / "run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()
