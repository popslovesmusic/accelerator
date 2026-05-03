import json
import os
import subprocess
import numpy as np
import argparse
from pathlib import Path

def generate_box_config(s, kappa, start_mode, seed, out_file):
    # Base config for structural_box_sim_cpp based on main.cpp logic
    config = {
        "nx": 256,
        "dt": 1.0e-4,
        "length": 1.0,
        "D_epsilon": 6.0e-4,
        "D_rho": 4.0e-4,
        "D_R": 2.0e-4,
        "a": 0.6,
        "b": 1.2,
        "c": 2.0,
        "alpha": 0.7,
        "beta": 0.8,
        "gamma": 1.2,
        "u": 0.15,
        "v": 0.08,
        "kappa": kappa,
        "lambda_R": 0.8,
        "s": s,
        "h": 0.08,
        "activity_thresh": 0.05,
        "initial_condition": {
            "seed": seed,
            "rho_base": 0.25,
            "residue_base": 0.0
        }
    }

    if start_mode == "cold":
        # Standard initiation search: just run at target s
        config["initial_condition"].update({
            "epsilon_kind": "uniform",
            "epsilon_base": 0.0,
            "noise_std": 0.01
        })
        config["steps"] = 20000 # Increased to allow for initiation
    else: # warm
        # Persistence search: use a sequence
        # Phase 1: Force initiation with high s
        # Phase 2: Drop to target s and see if it persists
        config["initial_condition"].update({
            "epsilon_kind": "gaussian",
            "epsilon_base": 0.0,
            "amplitude": 0.4,
            "sigma": 0.1,
            "offset": 0.0,
            "rho_base": 0.5,
            "residue_base": 0.2
        })
        config["sequence"] = [
            {"steps": 5000, "s": 0.5}, # Forced initiation
            {"steps": 15000, "s": s}     # Persistence test at target s
        ]
    
    with open(out_file, 'w') as f:
        json.dump(config, f, indent=2)

def generate_box_config_py(s, kappa, start_mode, seed, out_file):
    # Base config for structural_box_sim_v2 (Python)
    config = {
        "grid": {
            "nx": 128,
            "length": 1.0,
            "dt": 1.0e-4,
            "t_final": 2.0,
            "save_every": 500
        },
        "model": {
            "D_epsilon": 6.0e-4,
            "D_rho": 4.0e-4,
            "D_R": 2.0e-4,
            "a": 0.6,
            "b": 1.2,
            "c": 2.0,
            "alpha": 0.7,
            "beta": 0.8,
            "gamma": 1.2,
            "u": 0.15,
            "v": 0.08,
            "kappa": kappa,
            "lambda_R": 0.8,
            "s": s,
            "h": 0.08,
            "clamp_nonnegative": True,
            "epsilon_activity_threshold": 0.05
        },
        "initial_condition": {
            "seed": seed
        },
        "box": {
            "epsilon_max": 0.45,
            "rho_min": 0.0,
            "rho_max": 0.75,
            "residue_max": 0.38
        }
    }

    if start_mode == "cold":
        config["initial_condition"].update({
            "epsilon_kind": "zero",
            "rho_kind": "uniform",
            "rho_base": 0.1,
            "residue_kind": "zero"
        })
    else: # warm
        config["initial_condition"].update({
            "epsilon_kind": "gaussian_bump",
            "epsilon_base": 0.0,
            "epsilon_amplitude": 0.4,
            "epsilon_sigma": 0.1,
            "rho_kind": "uniform",
            "rho_base": 0.5,
            "residue_kind": "uniform",
            "residue_base": 0.2
        })
    
    with open(out_file, 'w') as f:
        json.dump(config, f, indent=2)

def generate_agent_config(mismatch_rate, kappa, start_mode, seed, out_file):
    # Base config for agent_based_sim_v1_cpp
    config = {
        "agent_count": 2000,
        "steps": 500, # Increased
        "dt": 0.05,
        "kappa": kappa,
        "R_c": 0.8,
        "K_phi": 1.0,
        "mismatch_rate": mismatch_rate,
        "residue_decay": 0.1,
        "seed": seed
    }

    if start_mode == "cold":
        config.update({
            "x_std": 2.0,
            "p_std": 2.0,
            "omega_mean": 1.0,
            "omega_std": 0.5
        })
    else: # warm
        config.update({
            "x_std": 0.01, # More ordered
            "p_std": 0.01,
            "omega_mean": 1.0,
            "omega_std": 0.2 # Increased to see drift
        })

    with open(out_file, 'w') as f:
        json.dump(config, f, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", choices=["box", "agent", "box_py"], required=True)
    parser.add_argument("--out_dir", required=True)
    parser.add_argument("--s_steps", type=int, default=5)
    parser.add_argument("--k_steps", type=int, default=5)
    parser.add_argument("--seeds", type=int, default=1)
    args = parser.parse_args()

    # Refined ranges based on preliminary results
    if "box" in args.tool:
        s_vals = np.linspace(0.0, 0.2, args.s_steps)
        k_vals = np.linspace(0.0, 2.0, args.k_steps)
    else:
        s_vals = np.linspace(0.0, 0.1, args.s_steps)
        k_vals = np.linspace(0.0, 1.5, args.k_steps)

    base_dir = Path(args.out_dir)
    os.makedirs(base_dir, exist_ok=True)

    results_index = []

    for seed_idx in range(args.seeds):
        seed = 1000 + seed_idx
        for s in s_vals:
            for kappa in k_vals:
                for mode in ["cold", "warm"]:
                    job_id = f"{args.tool}_{mode}_s{s:.4f}_k{kappa:.4f}_seed{seed}"
                    job_dir = base_dir / job_id
                    os.makedirs(job_dir, exist_ok=True)
                    
                    config_file = job_dir / "config.json"
                    if args.tool == "box":
                        generate_box_config(float(s), float(kappa), mode, seed, config_file)
                        cmd = f"python tools/structural_box_sim_cpp/sim_governed.py --config {config_file} --out {job_dir}"
                    elif args.tool == "box_py":
                        generate_box_config_py(float(s), float(kappa), mode, seed, config_file)
                        cmd = f"python tools/structural_box_sim_v2/sim.py --config {config_file} --out {job_dir}"
                    else:
                        generate_agent_config(float(s), float(kappa), mode, seed, config_file)
                        cmd = f"python tools/agent_based_sim_v1_cpp/sim_governed.py --config {config_file} --out {job_dir}"
                    
                    print(f"Running {job_id}...")
                    try:
                        subprocess.run(cmd, shell=True, check=True)
                        results_index.append({
                            "job_id": job_id,
                            "s": float(s),
                            "kappa": float(kappa),
                            "mode": mode,
                            "seed": seed,
                            "out_dir": str(job_dir)
                        })
                    except Exception as e:
                        print(f"Error running {job_id}: {e}")

    with open(base_dir / "results_index.json", 'w') as f:
        json.dump(results_index, f, indent=2)

if __name__ == "__main__":
    main()
