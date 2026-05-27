import os
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER"
DATA_DIR = RESULTS_DIR / "data"
ARTIFACTS_DIR = RESULTS_DIR / "artifacts"

SIGNAL_SCOPE_TOOL = REPO_ROOT / "tools/signal_scope_phase_continuation_engine/run_signal_scope.py"
STRUCTURAL_BOX_TOOL = REPO_ROOT / "tools/structural_box_sim_cpp/sim_governed.py"

def run_signal_scope(name, ablations=None, seed=20260527):
    print(f"--- Running Signal Scope: {name} ---")
    out_path = DATA_DIR / "signal_scope" / name
    out_path.mkdir(parents=True, exist_ok=True)
    
    config = {
        "id": f"cls_001_{name}",
        "engine": {
            "num_frames": 500,
            "num_nodes": 256,
            "engine_steps_per_frame": 5
        },
        "thresholds": {
            "mismatch_threshold": 0.015,
            "caution_threshold": 0.70,
            "signal_x_threshold": 0.60
        },
        "ablations": ablations or {}
    }
    
    config_path = out_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        
    cmd = [
        "python", str(SIGNAL_SCOPE_TOOL),
        "--config", str(config_path),
        "--out", str(out_path),
        "--seed", str(seed)
    ]
    
    subprocess.run(cmd, check=True)
    return out_path / "summary.json"

def run_structural_box(seed=20260527):
    print(f"--- Running Structural Box Baseline ---")
    out_path = DATA_DIR / "structural_box" / "baseline"
    out_path.mkdir(parents=True, exist_ok=True)
    
    config = {
        "nx": 256,
        "steps": 2000,
        "dt": 0.0001,
        "seed": seed,
        "D_epsilon": 0.0006,
        "D_rho": 0.0004,
        "D_R": 0.0002,
        "a": 0.6,
        "b": 1.2,
        "c": 2.0,
        "alpha": 0.7,
        "beta": 0.8,
        "gamma": 1.2,
        "u": 0.075,
        "v": 0.08,
        "kappa": 0.48,
        "lambda_R": 0.64,
        "s": 0.01,
        "h": 0.08,
        "activity_thresh": 0.05
    }
    
    config_path = out_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        
    cmd = [
        "python", str(STRUCTURAL_BOX_TOOL),
        "--config", str(config_path),
        "--out", str(out_path)
    ]
    
    subprocess.run(cmd, check=True)
    return out_path / "run_metadata.json"

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Signal Scope Suite
    runs = [
        ("baseline", {}),
        ("no_groove", {"disable_groove_memory": True}),
        ("no_induction", {"disable_inductive_layer": True}),
        ("no_residue", {"disable_residue": True}),
        ("shuffle_falsification", {"shuffle_input": True})
    ]
    
    signal_results = {}
    for name, abl in runs:
        summary_path = run_signal_scope(name, abl)
        with open(summary_path, "r") as f:
            signal_results[name] = json.load(f)
            
    # 2. Structural Box Cross-Verification
    run_structural_box()
    
    # 3. Save Aggregated Results
    with open(ARTIFACTS_DIR / "cls_001_results.json", "w") as f:
        json.dump(signal_results, f, indent=2)
        
    print("\n✅ CLS_001 Execution Complete.")

if __name__ == "__main__":
    main()
