import os
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER"
DATA_DIR = RESULTS_DIR / "data" / "cls_002"
ARTIFACTS_DIR = RESULTS_DIR / "artifacts"

STRUCTURAL_BOX_TOOL = REPO_ROOT / "tools/structural_box_sim_cpp/sim_governed.py"

def run_structural_box(name, override_config, sequence=None):
    print(f"--- Running Structural Box: {name} ---")
    out_path = DATA_DIR / name
    out_path.mkdir(parents=True, exist_ok=True)
    
    # Base config for Ratchet/Geometry validation
    config = {
        "nx": 512,
        "steps": 5000,
        "dt": 0.0001,
        "length": 1.0,
        "seed": 20260527,
        "epsilon_kind": "gaussian",
        "epsilon_base": 0.0,
        "amplitude": 0.5,
        "sigma": 0.05,
        "offset": 0.2, # Asymmetric initial offset
        
        "D_epsilon": 0.0006,
        "D_rho": 0.0004,
        "D_R": 0.0002,
        "a": 0.6,
        "b": 1.2,
        "c": 2.0,
        "alpha": 0.7,
        "beta": 0.8,
        "gamma": 1.2,
        "u": 0.15,
        "v": 0.08,
        "kappa": 0.48,
        "lambda_R": 0.64,
        "h": 0.08,
        "activity_thresh": 0.05
    }
    
    config.update(override_config)
    
    if sequence:
        config["sequence"] = sequence
    
    config_path = out_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        
    cmd = [
        "python", str(STRUCTURAL_BOX_TOOL),
        "--config", str(config_path),
        "--out", str(out_path)
    ]
    
    subprocess.run(cmd, check=True)
    
    # Extract the summary
    summary_file = out_path / "summary.json"
    if summary_file.exists():
        with open(summary_file, "r") as f:
            return json.load(f)
    return {}

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # 1. Baseline Geometry & Ratchet (Hysteresis Loop Sequence)
    # Ramp up 's' then ramp down
    ramp_seq = []
    for s_val in [0.0, 0.02, 0.05, 0.1, 0.05, 0.02, 0.0]:
        ramp_seq.append({"steps": 500, "s": s_val})
        
    results["baseline"] = run_structural_box("baseline", {}, sequence=ramp_seq)
    
    # 2. Falsification: Geometry Deformation (Increase Diffusion D_epsilon)
    results["geom_deformation"] = run_structural_box("geom_deformation", {
        "D_epsilon": 0.01 # Huge diffusion to destroy shape
    }, sequence=ramp_seq)
    
    # 3. Falsification: Gradient Inversion (u -> -u)
    results["gradient_inversion"] = run_structural_box("gradient_inversion", {
        "u": -0.15 # Invert ratchet direction
    }, sequence=ramp_seq)
    
    # 4. Falsification: Residue Lag Amplification (Increase decay lambda_R -> 5.0)
    results["residue_lag_amp"] = run_structural_box("residue_lag_amp", {
        "lambda_R": 5.0 # Fast decay destroys memory
    }, sequence=ramp_seq)
    
    # 5. Transport Bias validation (Zero Source, just initial pulse drift)
    # We don't use sequence here, just let it evolve for 5000 steps
    results["transport_bias"] = run_structural_box("transport_bias", {
        "steps": 5000,
        "s": 0.0
    })

    # Output Aggregation
    report_path = ARTIFACTS_DIR / "cls_002_results.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\n✅ CLS_002 Execution Complete. Results saved to {report_path}")

if __name__ == "__main__":
    main()
