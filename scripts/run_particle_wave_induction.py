import os
import json
import subprocess
from datetime import datetime
import numpy as np

# Campaign setup
campaign_id = "PARTICLE_WAVE_INDUCTION_V1"
run_dir = "results/2026-05-29_run01_Particle_Wave_Induction"
os.makedirs(run_dir, exist_ok=True)
data_dir = os.path.join(run_dir, "data")
artifacts_dir = os.path.join(run_dir, "artifacts")
os.makedirs(data_dir, exist_ok=True)
os.makedirs(artifacts_dir, exist_ok=True)

seeds = [101, 202, 303]

report = {
    "campaign_id": campaign_id,
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "results": {}
}

print(f"Starting Campaign: {campaign_id}")

def run_triadic(name, overrides):
    print(f"\n--- Running Triadic Closure: {name} ---")
    exp_dir = os.path.join(data_dir, "triadic_" + name)
    os.makedirs(exp_dir, exist_ok=True)
    
    summaries = []
    for seed in seeds:
        cfg = {
            "units": 1024,
            "steps": 2000,
            "structure": 3,
            "coupling_strength": 0.2,
            "coupling_symmetry": False,
            "admissibility_window": 0.85,
            "residue_diffusion_rate": 0.05,
            "seed": seed,
            "backend": "avx2"
        }
        cfg.update(overrides)
        
        cfg_path = os.path.join(exp_dir, f"cfg_seed_{seed}.json")
        out_path = os.path.join(exp_dir, f"out_seed_{seed}")
        os.makedirs(out_path, exist_ok=True)
        
        with open(cfg_path, 'w') as f:
            json.dump(cfg, f)
            
        cmd = ["python", "tools/triadic_closure_substrate_cpp/sim_governed.py", "--config", cfg_path, "--out", out_path]
        subprocess.run(cmd, capture_output=True, text=True)
        
        summary_file = os.path.join(out_path, "summary.json")
        if os.path.exists(summary_file):
            with open(summary_file, 'r') as f:
                summaries.append(json.load(f))
                
    if not summaries: return None
    agg = {}
    for k in summaries[0]["observables"].keys():
        vals = [s["observables"][k] for s in summaries if k in s["observables"]]
        if vals: agg[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}
    return agg

def run_pde(name, overrides):
    print(f"\n--- Running Procedural PDE: {name} ---")
    exp_dir = os.path.join(data_dir, "pde_" + name)
    os.makedirs(exp_dir, exist_ok=True)
    
    summaries = []
    for seed in seeds:
        cfg = {
            "nx": 128,
            "ny": 128,
            "steps": 1000,
            "diff_eps": 0.1,
            "diff_R": 0.05,
            "gamma_R": 0.8,
            "orient_smooth": 0.6,
            "A_min": 0.15,
            "seed": seed
        }
        cfg.update(overrides)
        
        cfg_path = os.path.join(exp_dir, f"cfg_seed_{seed}.json")
        out_path = os.path.join(exp_dir, f"out_seed_{seed}")
        os.makedirs(out_path, exist_ok=True)
        
        with open(cfg_path, 'w') as f:
            json.dump(cfg, f)
            
        # Procedural PDE engine is a compiled binary
        exe_path = "engines/procedural_pde_engine/build/Release/procedural_pde_engine"
        if os.name == 'nt': exe_path += ".exe"
        
        cmd = [exe_path, cfg_path, out_path]
        subprocess.run(cmd, capture_output=True, text=True)
        
        summary_file = os.path.join(out_path, "summary_metrics.json")
        if os.path.exists(summary_file):
            with open(summary_file, 'r') as f:
                summaries.append(json.load(f))
                
    if not summaries: return None
    agg = {}
    # Extract keys from the first summary object
    for k in summaries[0].keys():
        if isinstance(summaries[0][k], (int, float)):
            vals = [s[k] for s in summaries if k in s and isinstance(s[k], (int, float))]
            if vals: agg[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}
    return agg

# 1. Inductive Coupling (The Hypothesis)
report["results"]["triadic_inductive"] = run_triadic("inductive", {"coupling_symmetry": False})
report["results"]["pde_inductive"] = run_pde("inductive", {"gamma_R": 0.8})

# 2. Symmetric Control (The Schism / Failure Case)
report["results"]["triadic_symmetric"] = run_triadic("symmetric", {"coupling_symmetry": True})
report["results"]["pde_symmetric"] = run_pde("symmetric", {"gamma_R": 0.0})

# 3. Orientation Scramble (Falsification)
report["results"]["triadic_scramble"] = run_triadic("scramble", {"orientation_scramble": True})
report["results"]["pde_scramble"] = run_pde("scramble", {"orient_smooth": 0.0})

# Save report
report_path = os.path.join(artifacts_dir, "campaign_report.json")
with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)

print(f"\nCampaign Complete! Report: {report_path}")
