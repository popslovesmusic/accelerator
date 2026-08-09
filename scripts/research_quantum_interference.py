import os
import json
import subprocess
import pandas as pd
import numpy as np
import datetime
from pathlib import Path

# Metadata
RUN_ID = "research_quantum_interference_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
LOGS_DIR = OUTPUT_ROOT / "logs"
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_pde_two_packet_interference():
    # Parameters
    # s values near threshold
    s_vals = [0.08, 0.10, 0.12]
    # Spacing between IC packet and forcing packet center (relative to 0.5)
    spacings = [0.0, 0.05, 0.1, 0.2, 0.4] 
    seeds = [42, 43, 44]
    
    results = []
    
    base_config = {
        "nx": 512, # Higher resolution for "Quantum-Like" regime
        "dt": 1e-4,
        "length": 1.0,
        "D_epsilon": 6e-4,
        "D_rho": 4e-4,
        "D_R": 2e-4,
        "a": 0.6, "b": 1.2, "c": 2.0,
        "alpha": 0.7, "beta": 0.8, "gamma": 1.2,
        "u": 0.15, "v": 0.08,
        "kappa": 0.6, "lambda_R": 0.8, "h": 0.08,
        "steps": 4000,
        "s_duration": 2000,
        "activity_thresh": 0.05
    }

    for s in s_vals:
        for d in spacings:
            for seed in seeds:
                job_id = f"pde_interf_s_{s}_d_{d}_seed_{seed}"
                out_dir = JOBS_DIR / job_id
                os.makedirs(out_dir, exist_ok=True)
                
                config = base_config.copy()
                config["s"] = s
                # Packet 1 (IC) offset by d relative to Packet 2 (Forcing, centered at 0.5)
                # Main.cpp centers forcing at 0.5. IC offset is relative to 0.5.
                config["initial_condition"] = {
                    "epsilon_kind": "gaussian",
                    "amplitude": 0.4,
                    "sigma": 0.05, # Narrower packets for cleaner interference
                    "offset": d,
                    "seed": seed
                }
                
                with open(out_dir / "config.json", "w") as f:
                    json.dump(config, f, indent=2)
                
                print(f"[{datetime.datetime.now()}] [PDE] Running s={s}, d={d}, seed={seed}")
                cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(out_dir / "config.json"), "--out", str(out_dir)]
                
                with open(LOGS_DIR / f"{job_id}.stdout.log", "w") as f_out, \
                     open(LOGS_DIR / f"{job_id}.stderr.log", "w") as f_err:
                    subprocess.run(cmd, stdout=f_out, stderr=f_err)
                
                summary_path = out_dir / "summary.json"
                if summary_path.exists():
                    with open(summary_path, "r") as f:
                        summary = json.load(f)
                    metrics = summary["final_metrics"]
                    results.append({
                        "forcing_s": s,
                        "spacing_d": d,
                        "seed": seed,
                        "alignment_success_rate": metrics["alignment_success_rate"],
                        "residue_max": metrics["residue_max"]
                    })
    return results

def main():
    print(f"Starting Quantum-Like Interference Research: {RUN_ID}")
    
    results = run_pde_two_packet_interference()
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_ROOT / "quantum_interference_results.csv", index=False)
    
    # Synthesis: Alignment vs Spacing
    synthesis = df.groupby(["forcing_s", "spacing_d"])["alignment_success_rate"].mean().unstack(level=0)
    synthesis.to_csv(OUTPUT_ROOT / "interference_synthesis.csv")
    
    # Falsification: High spacing should revert to independent-sum behavior (or baseline)
    
    manifest = {
        "run_id": RUN_ID,
        "timestamp": datetime.datetime.now().isoformat(),
        "total_runs": len(results),
        "hypothesis": "Non-linear interference between phase packets based on spatial overlap.",
        "status": "completed"
    }
    with open(OUTPUT_ROOT / "run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Research run complete. Manifest saved to {OUTPUT_ROOT}/run_manifest.json")

if __name__ == "__main__":
    main()
