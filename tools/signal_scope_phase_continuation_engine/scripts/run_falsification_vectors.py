import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
TOOL_DIR = REPO_ROOT / "tools" / "signal_scope_phase_continuation_engine"
OUTPUT_ROOT = REPO_ROOT / "outputs" / "runs" / "signal_scope_falsification_campaign"

def run_sim(config_data, run_id, out_dir):
    config_path = out_dir / f"{run_id}_config.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)
    
    cmd = [
        sys.executable,
        str(TOOL_DIR / "run_signal_scope.py"),
        "--config", str(config_path),
        "--out", str(out_dir / run_id)
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    summary_path = out_dir / run_id / "summary.json"
    with open(summary_path, "r") as f:
        return json.load(f)

def main():
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    
    base_config = {
        "id": "falsification_base",
        "engine": {
            "num_frames": 200,
            "num_nodes": 100,
            "engine_steps_per_frame": 20
        },
        "ablations": {},
        "thresholds": {}
    }

    results = []

    # 0. Baseline
    print("\n--- Running Baseline ---")
    res_base = run_sim(base_config, "baseline", OUTPUT_ROOT)
    results.append({"vector": "baseline", "plv": res_base["metrics"]["phase_locking_value"], "mismatch": res_base["metrics"]["continuation_mismatch_mean"]})

    # 1. FV-1: Mechanism Substitution (Shuffle Control)
    print("\n--- Running FV-1 (Shuffle Control) ---")
    fv1_config = base_config.copy()
    fv1_config["ablations"] = {"shuffle_input": True}
    res_fv1 = run_sim(fv1_config, "fv1_shuffle", OUTPUT_ROOT)
    results.append({"vector": "FV-1", "plv": res_fv1["metrics"]["phase_locking_value"], "mismatch": res_fv1["metrics"]["continuation_mismatch_mean"]})

    # 2. FV-2: Boundary Collapse (Tight Thresholds)
    print("\n--- Running FV-2 (Boundary Collapse) ---")
    fv2_config = base_config.copy()
    fv2_config["thresholds"] = {"persistence_hard_mult": 0.5} # Extremely tight, should cause collapse
    res_fv2 = run_sim(fv2_config, "fv2_collapse", OUTPUT_ROOT)
    results.append({"vector": "FV-2", "plv": res_fv2["metrics"]["phase_locking_value"], "mismatch": res_fv2["metrics"]["continuation_mismatch_mean"]})

    # 3. FV-3: Primitive Reduction (Disable Residue)
    print("\n--- Running FV-3 (Primitive Reduction: No Residue) ---")
    fv3_config = base_config.copy()
    fv3_config["ablations"] = {"disable_residue": True}
    res_fv3 = run_sim(fv3_config, "fv3_reduction", OUTPUT_ROOT)
    results.append({"vector": "FV-3", "plv": res_fv3["metrics"]["phase_locking_value"], "mismatch": res_fv3["metrics"]["continuation_mismatch_mean"]})

    # 4. FV-4: Adversarial Initialization (High Initial Noise / Signal X bypass)
    print("\n--- Running FV-4 (Adversarial Initialization: Signal X bypass) ---")
    fv4_config = base_config.copy()
    fv4_config["ablations"] = {"disable_signal_x": True}
    res_fv4 = run_sim(fv4_config, "fv4_adversarial", OUTPUT_ROOT)
    results.append({"vector": "FV-4", "plv": res_fv4["metrics"]["phase_locking_value"], "mismatch": res_fv4["metrics"]["continuation_mismatch_mean"]})

    # Summary
    print("\n--- Falsification Summary ---")
    df = pd.DataFrame(results)
    print(df)
    
    report_path = OUTPUT_ROOT / "falsification_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nReport saved to {report_path}")

if __name__ == "__main__":
    main()
