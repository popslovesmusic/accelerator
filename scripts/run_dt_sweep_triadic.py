import json
import subprocess
import os
import numpy as np
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.utils.run_artifacts import create_run_dirs, make_run_id, write_report, write_resolved_config, write_run_metadata

def run_sim(dt, name):
    config = {
        "triads": 1024,
        "steps": int(10 / dt), # Normalize total simulation time to 10.0 units
        "dt": dt
    }
    config_path = write_resolved_config(RUN_DIRS.run_dir, f"dt_sweep_{name}_config", config)
    out_dir = RUN_DIRS.outputs_dir / f"dt_sweep_{name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["python", "tools/triadic_closure_substrate_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
    subprocess.run(cmd, capture_output=True, text=True)
    
    summary_path = out_dir / "summary.json"
    with open(summary_path, 'r') as f:
        return json.load(f)

SCRIPT_ID = "DT_SWEEP_TRIADIC_V1"
parser = argparse.ArgumentParser(description="Triadic dt sweep (artifact-hygienic).")
parser.add_argument("--run-id", default=None, help="Optional run id. Defaults to <timestamp>_<script_id>.")
parser.add_argument("--run-dir", "--out", dest="run_dir", default=None, help="Optional run directory root (contains configs/ outputs/ reports/ logs/ raw/).")
args = parser.parse_args()

if args.run_dir:
    run_dir = Path(args.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("configs", "outputs", "reports", "logs", "raw"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)
    RUN_DIRS = type("RunDirsShim", (), {})()
    RUN_DIRS.run_dir = run_dir
    RUN_DIRS.configs_dir = run_dir / "configs"
    RUN_DIRS.outputs_dir = run_dir / "outputs"
    RUN_DIRS.reports_dir = run_dir / "reports"
    RUN_DIRS.logs_dir = run_dir / "logs"
    RUN_DIRS.raw_dir = run_dir / "raw"
else:
    rid = args.run_id or make_run_id(SCRIPT_ID)
    RUN_DIRS = create_run_dirs(rid)

write_run_metadata(RUN_DIRS.run_dir, SCRIPT_ID, sys.argv)

dts = [0.1, 0.05, 0.01, 0.005]
results = {}

print(f"{'dt':<10} | {'Residue':<15} | {'Survival':<10} | {'Drift (%)':<10}")
print("-" * 55)

last_residue = None
for dt in dts:
    name = str(dt).replace(".", "")
    res = run_sim(dt, name)
    closure = res["observables"]["mean_closure_strength"]
    residue = res["observables"]["mean_residue_density"]
    survival = res["observables"]["survival_rate"]
    
    drift = 0.0
    if last_residue is not None:
        drift = abs(residue - last_residue) / last_residue * 100
    
    results[dt] = res
    print(f"{dt:<10} | {residue:<15.6f} | {survival:<10.3f} | {drift:<10.2f}")
    last_residue = residue

# Final verdict
final_drift = abs(results[0.005]["observables"]["mean_residue_density"] - results[0.01]["observables"]["mean_residue_density"]) / results[0.01]["observables"]["mean_residue_density"] * 100
print("-" * 55)
if final_drift < 0.5:
    print(f"VERDICT: Converged at dt=0.01 (Drift: {final_drift:.2f}%)")
else:
    print(f"VERDICT: NOT CONVERGED (Drift: {final_drift:.2f}%)")

write_report(RUN_DIRS.run_dir, "dt_sweep_results.json", results)
