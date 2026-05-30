import os
import json
import subprocess
import shutil
import concurrent.futures
from pathlib import Path
import itertools

# Paths
ENGINE_DIR = Path(__file__).resolve().parents[1]
BUILD_DIR = ENGINE_DIR / "build"
EXE_PATH = BUILD_DIR / "Release" / "procedural_pde_engine.exe"
if not EXE_PATH.exists():
    EXE_PATH = BUILD_DIR / "procedural_pde_engine.exe"
if not EXE_PATH.exists():
    EXE_PATH = BUILD_DIR / "procedural_pde_engine"

def run_seed(seed, config, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    config["seed"] = seed
    
    seed_config_path = out_dir / "config.json"
    with open(seed_config_path, "w") as f:
        json.dump(config, f, indent=2)
        
    cmd = [str(EXE_PATH.absolute()), str(seed_config_path.absolute()), str(out_dir.absolute())]
    subprocess.run(cmd, capture_output=True, text=True)
    
    summary_path = out_dir / "summary_metrics.json"
    if summary_path.exists():
        with open(summary_path, "r") as f:
            return json.load(f)
    return None

def run_campaign_stage(name, base_config, sweep_params, num_seeds, campaign_dir):
    stage_dir = campaign_dir / name
    stage_dir.mkdir(parents=True, exist_ok=True)
    
    keys = sweep_params.keys()
    values = sweep_params.values()
    combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    
    results = []
    print(f"\n--- Starting Stage: {name} ({len(combinations)} configs) ---")
    
    for i, combo in enumerate(combinations):
        config = base_config.copy()
        config.update(combo)
        
        config_id = f"config_{i}"
        config_dir = stage_dir / config_id
        
        print(f"Running config {i+1}/{len(combinations)}: {combo}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = {executor.submit(run_seed, seed, config, config_dir / f"seed_{seed}"): seed for seed in range(num_seeds)}
            for future in concurrent.futures.as_completed(futures):
                pass
        
        res = subprocess.run(["python", str(ENGINE_DIR / "scripts/analyze_outputs.py"), str(config_dir.absolute())], capture_output=True, text=True)
        if res.returncode == 0:
            try:
                summary = json.loads(res.stdout)
                summary["config"] = combo
                summary["config_id"] = config_id
                results.append(summary)
            except:
                print(f"Failed to parse analysis output for {config_id}")
            
    with open(stage_dir / "stage_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    return results

def main():
    campaign_dir = ENGINE_DIR / "outputs/runs/phase_1c_tuning"
    if campaign_dir.exists():
        shutil.rmtree(campaign_dir)
    campaign_dir.mkdir(parents=True)
    
    # Load Phase 1B best config as base for Phase 1C
    best_1b_path = ENGINE_DIR / "outputs/runs/phase_1b_tuning/phase_1b_best_config.json"
    if best_1b_path.exists():
        with open(best_1b_path, "r") as f:
            base_config = json.load(f)
    else:
        with open(ENGINE_DIR / "configs/pde_2d_baseline.json", "r") as f:
            base_config = json.load(f)
            
    # Add default Phase 1C params
    base_config.update({
        "gamma_R": 0.5,
        "coupling_write": 0.1,
        "fatigue": 0.05,
        "C_target": 0.5,
        "K_lock_threshold": 0.5,
        "K_unlock_threshold": 0.2,
        "lock_persistence_steps": 10
    })
    
    # Stage 1: Phase Coupling Discovery
    sweep_1 = {
        "K_lock_threshold": [0.3, 0.5, 0.7],
        "lock_persistence_steps": [5, 10, 20],
        "coupling_write": [0.05, 0.1, 0.2]
    }
    results_1 = run_campaign_stage("stage_1_phase_discovery", base_config, sweep_1, 8, campaign_dir)
    
    # Find best from stage 1 (max mean_phase_alignment * mean_mature_corridor_lifetime)
    best_1 = max(results_1, key=lambda x: x["mean_phase_alignment"] * x["mean_mature_corridor_lifetime"])
    print(f"Best Stage 1 Config: {best_1['config']}")
    
    # Stage 2: Saturation Control (Fatigue)
    stage_2_base = base_config.copy()
    stage_2_base.update(best_1["config"])
    sweep_2 = {
        "fatigue": [0.1, 0.5, 1.0, 2.0],
        "C_target": [0.1, 0.2, 0.3],
        "corridor_decay": [0.8, 0.9, 0.95]
    }
    results_2 = run_campaign_stage("stage_2_saturation_control", stage_2_base, sweep_2, 8, campaign_dir)
    
    # Best Stage 2: 0 < area_fraction < 0.6 and max mature_lifetime
    candidates = [r for r in results_2 if 0 < r["mean_corridor_area_fraction"] < 0.6]
    if not candidates: candidates = results_2
    best_2 = max(candidates, key=lambda x: x["mean_mature_corridor_lifetime"])
    print(f"Best Stage 2 Config: {best_2['config']} (area_frac: {best_2['mean_corridor_area_fraction']})")

    # Stage 4: Confirmatory Multiseed
    final_config = stage_2_base.copy()
    final_config.update(best_2["config"])
    final_config["seeds"] = 32
    
    print("\n--- Starting Stage 4: Confirmatory Multiseed ---")
    stage_4_dir = campaign_dir / "stage_4_confirmatory"
    stage_4_dir.mkdir(parents=True, exist_ok=True)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(run_seed, seed, final_config, stage_4_dir / f"seed_{seed}"): seed for seed in range(32)}
        for future in concurrent.futures.as_completed(futures):
            pass
            
    subprocess.run(["python", str(ENGINE_DIR / "scripts/analyze_outputs.py"), str(stage_4_dir.absolute())], check=True)

    with open(campaign_dir / "phase_1c_best_config.json", "w") as f:
        json.dump(final_config, f, indent=2)

    sweep_results = {
        "stage_1": results_1,
        "stage_2": results_2
    }
    with open(campaign_dir / "phase_1c_parameter_sweep_results.json", "w") as f:
        json.dump(sweep_results, f, indent=2)

    # Run Falsification
    print("\n--- Running Falsification Vectors ---")
    # Need to update falsification_harness.py to use phase_1c_best_config.json
    subprocess.run(["python", str(ENGINE_DIR / "scripts/falsification_harness.py")], check=True)

    print("\nPhase 1C Campaign Complete.")

if __name__ == "__main__":
    main()
