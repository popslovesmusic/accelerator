import os
import json
import subprocess
import pandas as pd
import numpy as np
import datetime
from pathlib import Path

# Metadata
RUN_ID = "research_hysteretic_falsification_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
LOGS_DIR = OUTPUT_ROOT / "logs"
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_falsification():
    # FV-3: kappa=0 (No memory/residue)
    s = 0.10 # Super-threshold for pre-conditioned, sub-threshold for baseline
    offset = 0.0
    seeds = [42, 43, 44]
    
    results = []
    
    base_config = {
        "nx": 256,
        "dt": 1e-4,
        "length": 1.0,
        "D_epsilon": 6e-4,
        "D_rho": 4e-4,
        "D_R": 2e-4,
        "a": 0.4, # Lowered gain to ensure IC packet decays without help
        "b": 1.2, "c": 2.0,
        "alpha": 0.7, "beta": 0.8, "gamma": 1.2,
        "u": 0.0, # NO RESIDUE COUPLING (Target of FV-3)
        "v": 0.08,
        "kappa": 0.6,
        "lambda_R": 0.8, "h": 0.08,
        "steps": 4000,
        "s_duration": 2000,
        "activity_thresh": 0.05
    }

    for seed in seeds:
        # Case 1: control (u=0, no packet)
        # Case 2: u=0, with packet (Tests Residual Epsilon)
        # Case 3: u=0.5, with packet (Tests Resided-Mediated Hysteresis)
        
        test_cases = [
            ("ctrl", 0.0, 0.0),
            ("u0_hyst", 0.4, 0.0),
            ("u05_hyst", 0.4, 0.5)
        ]

        for name, amp, u_val in test_cases:
            job_id = f"pde_fv3_{name}_seed_{seed}"
            out_dir = JOBS_DIR / job_id
            os.makedirs(out_dir, exist_ok=True)
            
            config = base_config.copy()
            config["u"] = u_val
            config["s"] = s
            config["initial_condition"] = {"epsilon_kind": "gaussian", "amplitude": amp, "sigma": 0.08, "offset": 0.0, "seed": seed}
            
            with open(out_dir / "config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            print(f"[{datetime.datetime.now()}] [FV-3] Running {job_id}")
            cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(out_dir / "config.json"), "--out", str(out_dir)]
            subprocess.run(cmd, capture_output=True)
            
            summary_path = out_dir / "summary.json"
            if summary_path.exists():
                with open(summary_path, "r") as f:
                    summary = json.load(f)
                results.append({
                    "vector": "FV-3",
                    "case": name,
                    "u": u_val,
                    "seed": seed,
                    "alignment_success_rate": summary["final_metrics"]["alignment_success_rate"]
                })

    return results

def main():
    print(f"Starting Hysteretic Falsification Research: {RUN_ID}")
    results = run_falsification()
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_ROOT / "falsification_results.csv", index=False)
    
    summary = df.groupby("case")["alignment_success_rate"].mean()
    print(summary)
    
    # HQLC Contrast = (u=0.5) - (u=0.0)
    hqlc_gain = summary.get("u05_hyst", 0) - summary.get("u00_hyst", summary.get("u0_hyst", 0))
    print(f"Residue-Mediated Gain: {hqlc_gain}")
    
    manifest = {
        "run_id": RUN_ID,
        "timestamp": datetime.datetime.now().isoformat(),
        "total_runs": len(results),
        "residue_mediated_gain": float(hqlc_gain),
        "status": "completed"
    }
    with open(OUTPUT_ROOT / "run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()
