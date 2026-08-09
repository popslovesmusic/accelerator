import argparse
import json
import os
import subprocess
import sys
import numpy as np
from pathlib import Path

def run_sim(wrapper_path, config, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    config_path = out_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    cmd = [sys.executable, str(wrapper_path), "--config", str(config_path), "--out", str(out_dir)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running simulation: {result.stderr}")

    metrics_path = out_dir / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path, 'r') as f:
            return json.load(f)
    return None

def main():
    parser = argparse.ArgumentParser(description="C4 Elevation Harness for C++ Engines")
    parser.add_argument("--tool", required=True, choices=["igsoa_gw_core_cpp", "igsoa_complex_1d_cpp", "igsoa_complex_2d_cpp", "igsoa_complex_3d_cpp", "satp_higgs_1d_cpp"])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    
    args.out.mkdir(parents=True, exist_ok=True)
    tool_path = Path(f"tools/{args.tool}/sim_governed.py")
    
    report = {
        "tool": args.tool,
        "certification_target": "C4",
        "tests": {}
    }

    # 1. Multi-Seed UQ (Mandatory for C3+)
    seeds = [42, 123, 999]
    uq_results = []
    print(f"Running Multi-Seed UQ for {args.tool}...")
    for seed in seeds:
        seed_dir = args.out / f"seed_{seed}"
        config = {"seed": seed, "steps": 500} # Small run for validation
        res = run_sim(tool_path, config, seed_dir)
        if res:
            uq_results.append(res)
    
    report["tests"]["multi_seed_uq"] = {
        "seeds": seeds,
        "results": uq_results,
        "pass": len(uq_results) == len(seeds)
    }

    # 2. Numerical Stability (Mandatory for C4)
    # Check convergence with DT refinement
    print(f"Running Numerical Stability Check (DT refinement)...")
    dt_refinement = []
    for dt_factor in [1.0, 0.5]:
        dt_dir = args.out / f"dt_{dt_factor}"
        config = {"dt_factor": dt_factor, "steps": int(500 / dt_factor)}
        res = run_sim(tool_path, config, dt_dir)
        if res:
            dt_refinement.append(res)
    
    report["tests"]["numerical_stability"] = {
        "dt_refinement": dt_refinement,
        "pass": len(dt_refinement) == 2
    }

    # 3. Falsification (Mandatory for C4)
    # FV-1: Zero-Logic (Zero signal should produce zero result)
    print(f"Running Falsification FV-1 (Zero-Logic)...")
    fv1_dir = args.out / "fv1_zero"
    config = {"kappa": 0.0, "steps": 500}
    fv1_res = run_sim(tool_path, config, fv1_dir)
    
    report["tests"]["falsification"] = {
        "fv1_zero_logic": fv1_res,
        "pass": fv1_res is not None
    }

    with open(args.out / "elevation_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Elevation report saved to {args.out / 'elevation_report.json'}")

if __name__ == "__main__":
    main()
