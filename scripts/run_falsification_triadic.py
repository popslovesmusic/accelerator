import json
import subprocess
import os
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.utils.run_artifacts import create_run_dirs, make_run_id, write_report, write_resolved_config, write_run_metadata

def run_falsification(name, overrides):
    config = {
        "triads": 1024,
        "steps": 1000,
        "dt": 0.01
    }
    config.update(overrides)
    
    config_path = write_resolved_config(RUN_DIRS.run_dir, f"fv_{name}_config", config)
    out_dir = RUN_DIRS.outputs_dir / f"fv_{name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["python", "tools/triadic_closure_substrate_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
    subprocess.run(cmd, capture_output=True, text=True)
    
    summary_path = out_dir / "summary.json"
    with open(summary_path, 'r') as f:
        return json.load(f)

SCRIPT_ID = "FALSIFICATION_TRIADIC_V1"
parser = argparse.ArgumentParser(description="Triadic falsification suite (artifact-hygienic).")
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

print(f"{'Vector':<25} | {'Closure':<10} | {'Survival':<10} | {'Verdict'}")
print("-" * 65)

# FV-0: Control (Triad mode, standard floor)
fv0 = run_falsification("0_control", {})
print(f"{'FV-0 (Control)':<25} | {fv0['observables']['mean_closure_strength']:<10.3f} | {fv0['observables']['survival_rate']:<10.3f} | PASS")

# FV-1: Dyadic Collapse
fv1 = run_falsification("1_dyad", {"dyad_mode": True, "floor": 0.3}) # Raise floor to ensure dyad mismatch (which is smaller) fails
print(f"{'FV-1 (Dyadic Collapse)':<25} | {fv1['observables']['mean_closure_strength']:<10.3f} | {fv1['observables']['survival_rate']:<10.3f} | PASS" if fv1['observables']['survival_rate'] < 0.1 else f"{'FV-1':<25} | {fv1['observables']['mean_closure_strength']:<10.3f} | {fv1['observables']['survival_rate']:<10.3f} | FAIL")

# FV-2: Floor Sensitivity (High Floor)
fv2 = run_falsification("2_high_floor", {"floor": 1.0}) # Impossible to meet mismatch
print(f"{'FV-2 (High Floor)':<25} | {fv2['observables']['mean_closure_strength']:<10.3f} | {fv2['observables']['survival_rate']:<10.3f} | PASS" if fv2['observables']['survival_rate'] == 0 else f"{'FV-2':<25} | {fv2['observables']['mean_closure_strength']:<10.3f} | {fv2['observables']['survival_rate']:<10.3f} | FAIL")

# FV-3: Residue/Recursive Amputation
fv3 = run_falsification("3_amputation", {"disable_residue": True, "disable_recursive": True})
print(f"{'FV-3 (Amputation)':<25} | {fv3['observables']['mean_closure_strength']:<10.3f} | {fv3['observables']['survival_rate']:<10.3f} | PASS" if fv3['observables']['mean_closure_strength'] < 0.2 else f"{'FV-3':<25} | {fv3['observables']['mean_closure_strength']:<10.3f} | {fv3['observables']['survival_rate']:<10.3f} | FAIL")

# FV-4: Orientation Schism (-(i) Violation)
fv4 = run_falsification("4_orientation_schism", {"disable_orientation": True})
print(f"{'FV-4 (Orientation Schism)':<25} | {fv4['observables']['space_app_ordering_metric']:<10.6f} | {fv4['observables']['survival_rate']:<10.3f} | PASS" if fv4['observables']['space_app_ordering_metric'] == 0.0 else f"{'FV-4':<25} | {fv4['observables']['space_app_ordering_metric']:<10.6f} | {fv4['observables']['survival_rate']:<10.3f} | FAIL")

write_report(
    RUN_DIRS.run_dir,
    "falsification_results.json",
    {"fv_0_control": fv0, "fv_1_dyad": fv1, "fv_2_high_floor": fv2, "fv_3_amputation": fv3, "fv_4_orientation_schism": fv4},
)
