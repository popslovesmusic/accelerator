import os
import json
import subprocess
import pandas as pd
import numpy as np
import datetime
from pathlib import Path

# Metadata
RUN_ID = "research_hysteretic_interference_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
LOGS_DIR = OUTPUT_ROOT / "logs"
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_pde_hysteresis():
    # Parameters
    # s_vals near threshold (0.08 - 0.12)
    s_vals = [0.08, 0.10, 0.12]
    # Spatial offsets: 0.0 (direct overlap), 0.2 (partial), 0.5 (separated)
    offsets = [0.0, 0.2, 0.5]
    seeds = [42, 43, 44]
    
    results = []
    
    base_config = {
        "nx": 256,
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
        for offset in offsets:
            for seed in seeds:
                # Case 1: Control (No prior packet)
                job_id_control = f"pde_ctrl_s_{s}_off_{offset}_seed_{seed}"
                out_dir_ctrl = JOBS_DIR / job_id_control
                os.makedirs(out_dir_ctrl, exist_ok=True)
                
                config_ctrl = base_config.copy()
                config_ctrl["s"] = s
                config_ctrl["initial_condition"] = {
                    "epsilon_kind": "gaussian",
                    "amplitude": 0.0, # NO PRIOR PACKET
                    "sigma": 0.08,
                    "seed": seed
                }
                
                with open(out_dir_ctrl / "config.json", "w") as f:
                    json.dump(config_ctrl, f, indent=2)
                
                # Case 2: Hysteretic (Prior packet at x=0.5)
                job_id_hyst = f"pde_hyst_s_{s}_off_{offset}_seed_{seed}"
                out_dir_hyst = JOBS_DIR / job_id_hyst
                os.makedirs(out_dir_hyst, exist_ok=True)
                
                config_hyst = base_config.copy()
                config_hyst["s"] = s
                # Packet 1 at center (0.5)
                # Packet 2 (forcing) will be centered at 0.5 + offset
                # (Main.cpp centers forcing at middle of grid, so we adjust IC to be at 0.5 - offset)
                config_hyst["initial_condition"] = {
                    "epsilon_kind": "gaussian",
                    "amplitude": 0.4, 
                    "sigma": 0.08,
                    "offset": -offset, # Offset packet 1 relative to forcing center
                    "seed": seed
                }
                
                with open(out_dir_hyst / "config.json", "w") as f:
                    json.dump(config_hyst, f, indent=2)

                # Run both
                for job_id, out_dir in [(job_id_control, out_dir_ctrl), (job_id_hyst, out_dir_hyst)]:
                    print(f"[{datetime.datetime.now()}] [PDE] Running {job_id}")
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
                            "case": "control" if "ctrl" in job_id else "hysteretic",
                            "forcing_s": s,
                            "spatial_offset": offset,
                            "seed": seed,
                            "alignment_success_rate": metrics["alignment_success_rate"],
                            "residue_max": metrics["residue_max"]
                        })

    return results

def run_agent_interference():
    # Phase packet interference in agents
    # Swarm coupling kappa
    k_vals = [0.4, 0.6, 0.8]
    seeds = [101, 102, 103]
    
    results = []
    
    for k in k_vals:
        for seed in seeds:
            job_id = f"agent_interf_k_{k}_seed_{seed}"
            out_dir = JOBS_DIR / job_id
            os.makedirs(out_dir, exist_ok=True)
            
            config = {
                "agent_count": 800,
                "steps": 2000,
                "R_c": 0.1,
                "K_phi": k,
                "seed": seed
            }
            with open(out_dir / "config.json", "w") as f:
                json.dump(config, f, indent=2)
                
            print(f"[{datetime.datetime.now()}] [Agent] Running {job_id}")
            cmd = ["python", "tools/agent_based_sim_v1_cpp/sim_governed.py", "--config", str(out_dir / "config.json"), "--out", str(out_dir)]
            subprocess.run(cmd, capture_output=True)
            
            summary_path = out_dir / "summary.json"
            if summary_path.exists():
                with open(summary_path, "r") as f:
                    summary = json.load(f)
                metrics = summary.get("final_metrics", summary.get("metrics", {}))
                results.append({
                    "mechanism": "agent",
                    "coupling_kappa": k,
                    "seed": seed,
                    "order_parameter": metrics.get("order_parameter", 0.0)
                })
    return results

def main():
    print(f"Starting Hysteretic Interference Research: {RUN_ID}")
    
    pde_results = run_pde_hysteresis()
    agent_results = run_agent_interference()
    
    pde_df = pd.DataFrame(pde_results)
    pde_df.to_csv(OUTPUT_ROOT / "pde_hysteresis_results.csv", index=False)
    
    agent_df = pd.DataFrame(agent_results)
    agent_df.to_csv(OUTPUT_ROOT / "agent_interference_results.csv", index=False)
    
    # Synthesis: Calculate Contrast
    # HQLC Contrast = (Alignment_Hyst - Alignment_Ctrl) / Alignment_Ctrl
    pde_summary = pde_df.groupby(["case", "forcing_s", "spatial_offset"])["alignment_success_rate"].mean().unstack(level=0)
    pde_summary["contrast"] = (pde_summary["hysteretic"] - pde_summary["control"]) / (pde_summary["control"] + 1e-9)
    pde_summary.to_csv(OUTPUT_ROOT / "pde_hqlc_synthesis.csv")
    
    # Falsification: Check contrast at high offset (should be 0)
    
    manifest = {
        "run_id": RUN_ID,
        "timestamp": datetime.datetime.now().isoformat(),
        "pde_runs": len(pde_results),
        "agent_runs": len(agent_results),
        "hypothesis": "Hysteretic Interference: Prior packets alter future admissibility.",
        "status": "completed"
    }
    with open(OUTPUT_ROOT / "run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Research run complete. Manifest saved to {OUTPUT_ROOT}/run_manifest.json")

if __name__ == "__main__":
    main()
