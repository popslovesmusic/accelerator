import os
import json
import pandas as pd
from pathlib import Path
import glob

RUN_ID = "phase_packets_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
JOBS_DIR = OUTPUT_ROOT / "jobs"

results = []
for summary_path in glob.glob(str(JOBS_DIR / "*" / "summary.json")):
    job_id = os.path.basename(os.path.dirname(summary_path))
    parts = job_id.split("_")
    model = parts[0]
    
    d = json.load(open(summary_path))
    
    if model == "pde":
        if "persistence" in job_id:
            mode = "persistence"
            s_val = 0.0
            k_idx = parts.index("k") + 1
            k_val = float(parts[k_idx])
            seed = int(parts[-1])
        else:
            mode = parts[1]
            s_idx = parts.index("s") + 1
            s_val = float(parts[s_idx])
            k_val = 0.6
            seed = int(parts[-1])
        af = d["final_metrics"].get("epsilon_active_fraction", 0.0)
    elif model == "abm":
        mode = "grid_sweep"
        m_idx = parts.index("m") + 1
        m_val = float(parts[m_idx])
        s_val = m_val
        k_idx = parts.index("k") + 1
        k_val = float(parts[k_idx])
        seed = int(parts[-1])
        af = d["final_metrics"].get("order_parameter", 0.0)
        
    results.append({
        "model": model, "mode": mode, "s_or_mismatch": s_val, "kappa": k_val, "seed": seed, "metric": af
    })

df = pd.DataFrame(results)
df.to_csv(OUTPUT_ROOT / "results.csv", index=False)
print("Research complete. Summary:")
print(df.groupby(["model", "mode", "s_or_mismatch", "kappa"]).mean().reset_index())
