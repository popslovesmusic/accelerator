import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
SIGNAL_SCOPE_DIR = REPO_ROOT / "tools" / "signal_scope_phase_continuation_engine"
KURAMOTO_DIR = REPO_ROOT / "tools" / "kuramoto_sim_v1"
OUTPUT_ROOT = REPO_ROOT / "outputs" / "runs" / "cross_mechanism_comparison"

def run_signal_scope(config_data, run_id):
    out_dir = OUTPUT_ROOT / "signal_scope" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    config_path = out_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)
    
    cmd = [
        sys.executable,
        str(SIGNAL_SCOPE_DIR / "run_signal_scope.py"),
        "--config", str(config_path),
        "--out", str(out_dir)
    ]
    subprocess.run(cmd, check=True)
    
    with open(out_dir / "summary.json", "r") as f:
        return json.load(f)

def run_kuramoto(config_data, run_id):
    out_dir = OUTPUT_ROOT / "kuramoto" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    config_path = out_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)
    
    cmd = [
        sys.executable,
        str(KURAMOTO_DIR / "sim.py"),
        "--config", str(config_path),
        "--out", str(out_dir)
    ]
    subprocess.run(cmd, check=True)
    
    with open(out_dir / "summary.json", "r") as f:
        return json.load(f)

def main():
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    
    # 1. Signal Scope Run
    ss_config = {
        "id": "cross_ss",
        "engine": {"num_frames": 500, "num_nodes": 100, "engine_steps_per_frame": 20},
        "ablations": {},
        "thresholds": {}
    }
    print("Running Signal Scope...")
    ss_res = run_signal_scope(ss_config, "default")
    
    # 2. Kuramoto Run
    k_config = {
        "n_oscillators": 100,
        "K": 2.0,
        "omega_dist": "gaussian",
        "omega_mean": 0.5,
        "omega_std": 0.1,
        "dt": 0.05,
        "steps": 1000,
        "seed": 101
    }
    print("Running Kuramoto...")
    k_res = run_kuramoto(k_config, "default")
    
    # 3. Comparison
    comparison = {
        "signal_scope": {
            "metric_name": "phase_locking_value",
            "value": ss_res["metrics"]["phase_locking_value"]
        },
        "kuramoto": {
            "metric_name": "order_parameter",
            "value": k_res["final_metrics"]["order_parameter"]
        }
    }
    
    print("\n--- Cross-Mechanism Comparison ---")
    print(json.dumps(comparison, indent=2))
    
    with open(OUTPUT_ROOT / "comparison_report.json", "w") as f:
        json.dump(comparison, f, indent=2)

if __name__ == "__main__":
    main()
