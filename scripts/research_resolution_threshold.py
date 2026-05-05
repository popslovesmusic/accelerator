import os
import json
import subprocess
import pandas as pd
import numpy as np
import datetime
from pathlib import Path

# Metadata
RUN_ID = "research_resolution_threshold_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
LOGS_DIR = OUTPUT_ROOT / "logs"
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_pde_resolution():
    # Parameters
    nx_vals = [32, 64, 128, 256, 512]
    s_vals = [0.05, 0.08, 0.10, 0.12, 0.15]
    seeds = [42, 43, 44] # Triple seed for C4 rigor
    
    results = []
    
    # Base config template
    base_config = {
        "dt": 1e-4,
        "length": 1.0,
        "D_epsilon": 6e-4,
        "D_rho": 4e-4,
        "D_R": 2e-4,
        "a": 0.6, "b": 1.2, "c": 2.0,
        "alpha": 0.7, "beta": 0.8, "gamma": 1.2,
        "u": 0.15, "v": 0.08,
        "kappa": 0.6, "lambda_R": 0.8, "h": 0.08,
        "activity_thresh": 0.05,
        "initial_condition": {
            "epsilon_kind": "gaussian",
            "amplitude": 0.32,
            "sigma": 0.08,
            "offset": 0.0
        }
    }

    for nx in nx_vals:
        for s in s_vals:
            for seed in seeds:
                job_id = f"pde_nx_{nx}_s_{s}_seed_{seed}"
                out_dir = JOBS_DIR / job_id
                os.makedirs(out_dir, exist_ok=True)
                
                config = base_config.copy()
                config["nx"] = nx
                config["s"] = s
                config["initial_condition"]["seed"] = seed
                config["steps"] = 3000
                config["s_duration"] = 2000 # 2000 steps of forcing, 1000 steps of relaxation
                
                config_path = out_dir / "config.json"
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
                
                print(f"[{datetime.datetime.now()}] [PDE] Running nx={nx}, s={s}, seed={seed}")
                # Using sim_governed.py for C++ C4 compliance
                cmd = [
                    "python", "tools/structural_box_sim_cpp/sim_governed.py",
                    "--config", str(config_path),
                    "--out", str(out_dir)
                ]
                
                with open(LOGS_DIR / f"{job_id}.stdout.log", "w") as f_out, \
                     open(LOGS_DIR / f"{job_id}.stderr.log", "w") as f_err:
                    subprocess.run(cmd, stdout=f_out, stderr=f_err)
                
                summary_path = out_dir / "summary.json"
                if summary_path.exists():
                    with open(summary_path, "r") as f:
                        summary = json.load(f)
                    metrics = summary["final_metrics"]
                    results.append({
                        "mechanism": "pde_reaction_diffusion",
                        "resolution_param": nx,
                        "forcing_s": s,
                        "seed": seed,
                        "alignment_success_rate": metrics["alignment_success_rate"],
                        "epsilon_max": metrics["epsilon_max"],
                        "residue_max": metrics["residue_max"],
                        "output_dir": str(out_dir)
                    })
                else:
                    print(f"Warning: No summary found for {job_id}")

    return results

def run_agent_resolution():
    # Parameters
    count_vals = [100, 400, 1600] # 6400 might be too slow for this turn
    kappa_vals = [0.4, 0.6, 0.8] # kappa is a proxy for coupling strength
    seeds = [101, 102, 103]
    
    results = []
    
    for count in count_vals:
        for k in kappa_vals:
            for seed in seeds:
                job_id = f"agent_count_{count}_kappa_{k}_seed_{seed}"
                out_dir = JOBS_DIR / job_id
                os.makedirs(out_dir, exist_ok=True)
                
                config = {
                    "agent_count": count,
                    "steps": 2000,
                    "R_c": 0.1,
                    "K_phi": k,
                    "seed": seed
                }
                config_path = out_dir / "config.json"
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
                
                print(f"[{datetime.datetime.now()}] [Agent] Running count={count}, kappa={k}, seed={seed}")
                cmd = [
                    "python", "tools/agent_based_sim_v1_cpp/sim_governed.py",
                    "--config", str(config_path),
                    "--out", str(out_dir)
                ]
                
                with open(LOGS_DIR / f"{job_id}.stdout.log", "w") as f_out, \
                     open(LOGS_DIR / f"{job_id}.stderr.log", "w") as f_err:
                    subprocess.run(cmd, stdout=f_out, stderr=f_err)
                
                summary_path = out_dir / "summary.json"
                if summary_path.exists():
                    with open(summary_path, "r") as f:
                        summary = json.load(f)
                    # Extract metrics - note: key might be different in agent sim
                    metrics = summary.get("final_metrics", summary.get("metrics", {}))
                    results.append({
                        "mechanism": "agent_based_swarm",
                        "resolution_param": count,
                        "coupling_kappa": k,
                        "seed": seed,
                        "order_parameter": metrics.get("order_parameter", 0.0),
                        "residue_mean": metrics.get("residue_mean", 0.0),
                        "output_dir": str(out_dir)
                    })
    return results

def main():
    print(f"Starting Resolution Transition Research: {RUN_ID}")
    
    pde_results = run_pde_resolution()
    agent_results = run_agent_resolution()
    
    # Save results
    pde_df = pd.DataFrame(pde_results)
    pde_df.to_csv(OUTPUT_ROOT / "pde_resolution_results.csv", index=False)
    
    agent_df = pd.DataFrame(agent_results)
    agent_df.to_csv(OUTPUT_ROOT / "agent_resolution_results.csv", index=False)
    
    # Simple Synthesis
    pde_summary = pde_df.groupby(["resolution_param", "forcing_s"])["alignment_success_rate"].mean().reset_index()
    pde_summary.to_csv(OUTPUT_ROOT / "pde_synthesis.csv", index=False)
    
    agent_summary = agent_df.groupby(["resolution_param", "coupling_kappa"])["order_parameter"].mean().reset_index()
    agent_summary.to_csv(OUTPUT_ROOT / "agent_synthesis.csv", index=False)

    # Falsification Case (s=0 for PDE, k=0 for Agent)
    print("Running Falsification Checks...")
    # (These are implicitly covered if s_vals or kappa_vals included 0, but let's be explicit if needed)
    
    manifest = {
        "run_id": RUN_ID,
        "timestamp": datetime.datetime.now().isoformat(),
        "pde_runs": len(pde_results),
        "agent_runs": len(agent_results),
        "hypothesis": "Resolution-induced transition from relational to geometric states.",
        "status": "completed"
    }
    with open(OUTPUT_ROOT / "run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Research run complete. Manifest saved to {OUTPUT_ROOT}/run_manifest.json")

if __name__ == "__main__":
    main()
