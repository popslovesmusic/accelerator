
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

RUN_ID = "two_threshold_rigor_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
JOBS_DIR = OUTPUT_ROOT / "jobs"

def aggregate():
    results = []
    
    # 1. PDE Initiation
    summary_files = list(JOBS_DIR.glob("pde_init_s_*/summary.json")) + list(JOBS_DIR.glob("pde_init_s_*/**/summary.json"))
    seen = set()
    for f in summary_files:
        if f in seen: continue
        seen.add(f)
        try:
            d = json.load(open(f))
            s = d["config"]["model"]["s"]
            seed = d["config"]["initial_condition"]["seed"]
            results.append({
                "mechanism": "pde", "type": "initiation", "s": s, "kappa": 0.6, "seed": seed,
                "active_fraction": d["final"]["epsilon_active_fraction"],
                "epsilon_max": d["final"]["epsilon_max"]
            })
        except: pass

    # 2. PDE Persistence
    summary_files = list(JOBS_DIR.glob("pde_pers_k_*/summary.json"))
    for f in summary_files:
        try:
            d = json.load(open(f))
            k = d["config"]["kappa"]
            seed = d["config"]["seed"]
            fals_res = d["report"]["falsification_zero_s"]
            results.append({
                "mechanism": "pde", "type": "persistence", "s": 0.0, "kappa": k, "seed": seed,
                "active_fraction": fals_res["epsilon_active_fraction"],
                "epsilon_max": fals_res["epsilon_max"]
            })
        except: pass
        
    # 3. ABM (if any)
    summary_files = list(JOBS_DIR.glob("abm_*/summary.json"))
    for f in summary_files:
        try:
            d = json.load(open(f))
            mr = d["config"].get("mismatch_rate", np.nan)
            k = d["config"].get("kappa", np.nan)
            seed = d["config"]["seed"]
            type_str = "initiation" if "init" in f.parent.name else "persistence"
            results.append({
                "mechanism": "agent", "type": type_str, "s": np.nan, "mismatch_rate": mr, "kappa": k, "seed": seed,
                "active_fraction": d["final_metrics"]["order_parameter"]
            })
        except: pass

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_ROOT / "raw_results.csv", index=False)
    group_cols = ["mechanism", "type", "s", "kappa", "mismatch_rate"]
    for col in group_cols:
        if col not in df.columns: df[col] = np.nan
    summary_df = df.groupby(group_cols, dropna=False).mean().reset_index()
    summary_df.to_csv(OUTPUT_ROOT / "summary_results.csv", index=False)
    print("Aggregation complete.")
    print(summary_df)

if __name__ == "__main__":
    aggregate()
