import json
import subprocess
import os
import numpy as np

def run_sim(dt, name):
    config = {
        "triads": 1024,
        "steps": int(10 / dt), # Normalize total simulation time to 10.0 units
        "dt": dt
    }
    config_path = f"dt_sweep_{name}_config.json"
    out_dir = f"dt_sweep_{name}_out"
    os.makedirs(out_dir, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f)
        
    cmd = ["python", "tools/triadic_closure_substrate_cpp/sim_governed.py", "--config", config_path, "--out", out_dir]
    subprocess.run(cmd, capture_output=True, text=True)
    
    summary_path = os.path.join(out_dir, "summary.json")
    with open(summary_path, 'r') as f:
        return json.load(f)

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
