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

def run_uq(seed):
    config = {
        "triads": 1024,
        "steps": 1000,
        "dt": 0.01,
        "seed": seed
    }
    
    config_path = write_resolved_config(RUN_DIRS.run_dir, f"uq_seed_{seed}_config", config)
    out_dir = RUN_DIRS.outputs_dir / f"uq_seed_{seed}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["python", "tools/triadic_closure_substrate_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
    subprocess.run(cmd, capture_output=True, text=True)
    
    summary_path = out_dir / "summary.json"
    with open(summary_path, 'r') as f:
        return json.load(f)

SCRIPT_ID = "UQ_TRIADIC_V1"
parser = argparse.ArgumentParser(description="Triadic uncertainty quantification (artifact-hygienic).")
parser.add_argument("--seed-start", type=int, default=42, help="First seed (inclusive).")
parser.add_argument("--seed-count", type=int, default=10, help="Number of seeds.")
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

write_run_metadata(RUN_DIRS.run_dir, SCRIPT_ID, sys.argv, extra={"seed_start": args.seed_start, "seed_count": args.seed_count})

seeds = range(args.seed_start, args.seed_start + args.seed_count)
closures = []
residues = []
survivals = []

print(f"Running 10-seed ensemble...")

for seed in seeds:
    res = run_uq(seed)
    closures.append(res["observables"]["mean_closure_strength"])
    residues.append(res["observables"]["mean_residue_density"])
    survivals.append(res["observables"]["survival_rate"])

print("-" * 40)
print(f"Closure:  {np.mean(closures):.6f} +/- {np.std(closures):.6f}")
print(f"Residue:  {np.mean(residues):.6f} +/- {np.std(residues):.6f}")
print(f"Survival: {np.mean(survivals):.6f} +/- {np.std(survivals):.6f}")
print("-" * 40)

write_report(
    RUN_DIRS.run_dir,
    "uq_ensemble_summary.json",
    {
        "seed_start": args.seed_start,
        "seed_count": args.seed_count,
        "closure_mean": float(np.mean(closures)),
        "closure_std": float(np.std(closures)),
        "residue_mean": float(np.mean(residues)),
        "residue_std": float(np.std(residues)),
        "survival_mean": float(np.mean(survivals)),
        "survival_std": float(np.std(survivals)),
    },
)
