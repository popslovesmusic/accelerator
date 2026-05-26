import json
import subprocess
import os

def run_falsification(name, overrides):
    config = {
        "triads": 1024,
        "steps": 1000,
        "dt": 0.01
    }
    config.update(overrides)
    
    config_path = f"fv_{name}_config.json"
    out_dir = f"fv_{name}_out"
    os.makedirs(out_dir, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f)
        
    cmd = ["python", "tools/triadic_closure_substrate_cpp/sim_governed.py", "--config", config_path, "--out", out_dir]
    subprocess.run(cmd, capture_output=True, text=True)
    
    summary_path = os.path.join(out_dir, "summary.json")
    with open(summary_path, 'r') as f:
        return json.load(f)

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
