import os
import json
import pandas as pd
from pathlib import Path
import glob

RUN_ID = "hysteretic_interference_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
JOBS_DIR = OUTPUT_ROOT / "jobs"

results = []
for summary_path in glob.glob(str(JOBS_DIR / "*" / "summary.json")):
    d = json.load(open(summary_path))
    job_id = os.path.basename(os.path.dirname(summary_path))
    parts = job_id.split("_")
    
    # job_id looks like: preconditioned_pos_s_0.02_seed_1
    # parts: ['preconditioned', 'pos', 's', '0.02', 'seed', '1']
    if parts[0] == "baseline":
        mode = "baseline"
        s_test = float(parts[2])
        seed = int(parts[4])
    else:
        mode = f"{parts[0]}_{parts[1]}"
        s_test = float(parts[3])
        seed = int(parts[5])
    
    m = d["final_metrics"]
    results.append({
        "mode": mode,
        "s_test": s_test,
        "seed": seed,
        "epsilon_max": m["epsilon_max"],
        "epsilon_min": m.get("epsilon_min", 0.0),
        "active_fraction": m["epsilon_active_fraction"]
    })

df = pd.DataFrame(results)
df.to_csv(OUTPUT_ROOT / "aggregated_results.csv", index=False)

# Calculate s_crit
# We define s_crit as the minimum |s_test| where mean active_fraction > 0.1
summary = df.groupby(["mode", "s_test"]).mean(numeric_only=True).reset_index()

print("Interference Analysis Summary:")
print(summary)

# Export summary
summary.to_csv(OUTPUT_ROOT / "summary_analysis.csv", index=False)
