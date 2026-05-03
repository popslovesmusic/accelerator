
import os
import json
import subprocess
import pandas as pd
from pathlib import Path

RUN_ID = "two_threshold_rigor_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
JOBS_DIR = OUTPUT_ROOT / "jobs"

def run_long_pers():
    kappa_vals = [0.0, 1.0]
    results = []
    for k in kappa_vals:
        job_id = f"pde_pers_long_k_{k}"
        out_dir = JOBS_DIR / job_id
        out_dir.mkdir(parents=True, exist_ok=True)
        config = {"nx": 128, "steps": 500000, "kappa": k, "s": 0.0, "seed": 42}
        config_path = out_dir / "config.json"
        with open(config_path, "w") as f: json.dump(config, f, indent=2)
        cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py", "--config", str(config_path), "--out", str(out_dir)]
        print(f"Running {job_id}...")
        subprocess.run(cmd, capture_output=True)
        summary_path = out_dir / "summary.json"
        if summary_path.exists():
            d = json.load(open(summary_path))
            fals_res = d["report"]["falsification_zero_s"]
            results.append({"kappa": k, "active_fraction": fals_res["epsilon_active_fraction"]})
    print(results)

if __name__ == "__main__":
    run_long_pers()
