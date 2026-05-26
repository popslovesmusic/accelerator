import json
import subprocess
import os
import numpy as np

def run_uq(seed):
    config = {
        "triads": 1024,
        "steps": 1000,
        "dt": 0.01,
        "seed": seed
    }
    
    config_path = f"uq_seed_{seed}_config.json"
    out_dir = f"uq_seed_{seed}_out"
    os.makedirs(out_dir, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f)
        
    cmd = ["python", "tools/triadic_closure_substrate_cpp/sim_governed.py", "--config", config_path, "--out", out_dir]
    subprocess.run(cmd, capture_output=True, text=True)
    
    summary_path = os.path.join(out_dir, "summary.json")
    with open(summary_path, 'r') as f:
        return json.load(f)

seeds = range(42, 52) # 10 seeds
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
