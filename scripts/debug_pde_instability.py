import json
import os
import subprocess
import numpy as np
import pandas as pd
from pathlib import Path

def run_comparison():
    out_dir = Path("outputs/debug/pde_instability_test")
    os.makedirs(out_dir, exist_ok=True)

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
        "kappa": 0.6,
        "lambda_R": 0.8,
        "s": 0.1, # Strong forcing to ensure initiation
        "h": 0.08,
        "activity_thresh": 0.05,
        "initial_condition": {
            "seed": 1000,
            "epsilon_kind": "gaussian", # for C++
            "epsilon_base": 0.0,
            "amplitude": 0.4,
            "sigma": 0.1,
            "offset": 0.0,
            "rho_base": 0.25,
            "residue_base": 0.0
        },
        "steps": 20000
    }

    # Python config needs slightly different names for some init fields
    config_py = {
        "grid": {
            "nx": config["nx"],
            "dt": config["dt"],
            "length": config["length"],
            "t_final": config["steps"] * config["dt"],
            "save_every": 100
        },
        "model": {
            "D_epsilon": config["D_epsilon"],
            "D_rho": config["D_rho"],
            "D_R": config["D_R"],
            "a": config["a"],
            "b": config["b"],
            "c": config["c"],
            "alpha": config["alpha"],
            "beta": config["beta"],
            "gamma": config["gamma"],
            "u": config["u"],
            "v": config["v"],
            "kappa": config["kappa"],
            "lambda_R": config["lambda_R"],
            "s": config["s"],
            "h": config["h"],
            "clamp_nonnegative": True,
            "epsilon_activity_threshold": config["activity_thresh"]
        },
        "initial_condition": {
            "seed": config["initial_condition"]["seed"],
            "epsilon_kind": "gaussian_bump",
            "epsilon_base": config["initial_condition"]["epsilon_base"],
            "epsilon_amplitude": config["initial_condition"]["amplitude"],
            "epsilon_sigma": config["initial_condition"]["sigma"],
            "epsilon_offset": config["initial_condition"]["offset"],
            "rho_kind": "uniform",
            "rho_base": config["initial_condition"]["rho_base"],
            "residue_kind": "zero"
        },
        "box": {
            "epsilon_max": 10.0, # Large enough to not matter
            "rho_min": -10.0,
            "rho_max": 10.0,
            "residue_max": 10.0
        }
    }

    cpp_dir = out_dir / "cpp"
    py_dir = out_dir / "py"
    os.makedirs(cpp_dir, exist_ok=True)
    os.makedirs(py_dir, exist_ok=True)

    with open(cpp_dir / "config.json", 'w') as f:
        json.dump(config, f, indent=2)
    with open(py_dir / "config.json", 'w') as f:
        json.dump(config_py, f, indent=2)

    print("Running C++ simulation...")
    cpp_cmd = f"python tools/structural_box_sim_cpp/sim_governed.py --config {cpp_dir.absolute()}/config.json --out {cpp_dir.absolute()}"
    subprocess.run(cpp_cmd, shell=True, check=True)

    print("Running Python simulation...")
    py_cmd = f"python tools/structural_box_sim_v2/sim.py --config {py_dir.absolute()}/config.json --out {py_dir.absolute()}"
    subprocess.run(py_cmd, shell=True, check=True)

    # Compare results
    with open(cpp_dir / "summary.json", 'r') as f:
        cpp_res = json.load(f)["final_metrics"]
    with open(py_dir / "summary.json", 'r') as f:
        py_res = json.load(f)["final"]

    print("\nComparison Results:")
    print(f"{'Metric':<25} | {'C++ (FP64)':<15} | {'Python':<15} | {'Diff':<15}")
    print("-" * 75)
    for k in ["epsilon_max", "rho_min", "residue_max", "epsilon_active_fraction"]:
        v_cpp = cpp_res[k]
        v_py = py_res[k]
        diff = abs(v_cpp - v_py)
        print(f"{k:<25} | {v_cpp:<15.6f} | {v_py:<15.6f} | {diff:<15.6e}")

if __name__ == "__main__":
    run_comparison()
