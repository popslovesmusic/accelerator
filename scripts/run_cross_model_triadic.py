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

def run_triadic():
    config = {"triads": 1024, "steps": 1000, "dt": 0.01, "seed": 42}
    config_path = write_resolved_config(RUN_DIRS.run_dir, "cross_triadic_config", config)
    out_dir = RUN_DIRS.outputs_dir / "cross_triadic"
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["python", "tools/triadic_closure_substrate_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)], capture_output=True)
    with open(out_dir / "summary.json", 'r') as f: return json.load(f)

def run_optical():
    # Optical Reservoir baseline
    cmd = ["python", "tools/optical_reservoir/simulate_optical_reservoir.py", "--steps", "1000", "--dt", "0.01", "--triads", "3", "--feedback", "--network-mode", "triad_network"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    # Optical Reservoir outputs JSON to stdout in triad_network mode
    # But wait, earlier I saw it might have UTF-16 BOM or other issues if redirected.
    # Let's try to capture it cleanly.
    return json.loads(res.stdout.strip().lstrip('\ufeff'))

SCRIPT_ID = "CROSS_MODEL_TRIADIC_V1"
parser = argparse.ArgumentParser(description="Cross-model comparison (artifact-hygienic).")
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

print("Running cross-model comparison...")
triadic = run_triadic()
optical = run_optical()

t_sync = triadic["observables"]["space_app_ordering_metric"]
o_sync = optical["network"]["synchronization_index"]

print("-" * 50)
print(f"Triadic Closure Ordering: {t_sync:.6f}")
print(f"Optical Reservoir Sync:   {o_sync:.6f}")
print("-" * 50)

# Qualitative assessment
if abs(t_sync - o_sync) < 0.5:
    print("VERDICT: Qualitative Alignment Confirmed (Mechanism Independence Supported)")
else:
    print("VERDICT: Divergent behavior observed (Requires further investigation)")

write_report(RUN_DIRS.run_dir, "cross_model_results.json", {"triadic": triadic, "optical": optical})
