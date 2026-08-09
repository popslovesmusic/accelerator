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
    
    # Generate all combinations of sweep parameters
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
        
        # Run seeds in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = {executor.submit(run_seed, seed, config, config_dir / f"seed_{seed}"): seed for seed in range(num_seeds)}
            for future in concurrent.futures.as_completed(futures):
                pass # Wait for completion
        
        # Analyze config
        res = subprocess.run(["python", str(ENGINE_DIR / "scripts/analyze_outputs.py"), str(config_dir.absolute())], capture_output=True, text=True)
        if res.returncode == 0:
            summary = json.loads(res.stdout)
            summary["config"] = combo
            summary["config_id"] = config_id
            results.append(summary)
            
    # Save stage summary
    with open(stage_dir / "stage_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    return results

def main():
    campaign_dir = ENGINE_DIR / "outputs/runs/phase_1b_tuning"
    if campaign_dir.exists():
        shutil.rmtree(campaign_dir)
    campaign_dir.mkdir(parents=True)
    
    # Load baseline config
    with open(ENGINE_DIR / "configs/pde_2d_baseline.json", "r") as f:
        base_config = json.load(f)
    
    # Stage 1: Threshold Discovery
    sweep_1 = {
        "R_corridor_threshold": [0.000001, 0.000005, 0.00001],
        "corridor_on_threshold": [0.00001, 0.00005, 0.0001],
        "corridor_off_threshold": [0.000005, 0.00001]
    }
    results_1 = run_campaign_stage("stage_1_threshold_discovery", base_config, sweep_1, 8, campaign_dir)
    
    # Find best from stage 1 (max proto_corridor_lifetime)
    best_1 = max(results_1, key=lambda x: x["mean_proto_corridor_lifetime"])
    print(f"Best Stage 1 Config: {best_1['config']} (proto_lifetime: {best_1['mean_proto_corridor_lifetime']})")
    
    # Stage 2: Reinforcement Sweep
    stage_2_base = base_config.copy()
    stage_2_base.update(best_1["config"])
    sweep_2 = {
        "write_rate_R": [0.05, 0.10, 0.20],
        "reinforcement_gain": [0.02, 0.05, 0.10],
        "corridor_decay": [0.95, 0.98],
        "corridor_gain": [0.1, 0.2]
    }
    results_2 = run_campaign_stage("stage_2_reinforcement_sweep", stage_2_base, sweep_2, 8, campaign_dir)
    
    # Find best from stage 2 (max mean_corridor_lifetime)
    best_2 = max(results_2, key=lambda x: x["mean_corridor_lifetime"])
    print(f"Best Stage 2 Config: {best_2['config']} (corridor_lifetime: {best_2['mean_corridor_lifetime']})")

    # Stage 3: Diffusion / Orientation Sweep
    stage_3_base = stage_2_base.copy()
    stage_3_base.update(best_2["config"])
    sweep_3 = {
        "diff_eps": [0.10, 0.05, 0.01],
        "diff_R": [0.01, 0.005, 0.0],
        "orient_smooth": [0.25, 0.50, 0.75]
    }
    results_3 = run_campaign_stage("stage_3_diffusion_orientation_sweep", stage_3_base, sweep_3, 8, campaign_dir)
    
    # Find best from stage 3
    best_3 = max(results_3, key=lambda x: x["mean_corridor_lifetime"])
    print(f"Best Stage 3 Config: {best_3['config']} (corridor_lifetime: {best_3['mean_corridor_lifetime']})")

    # Stage 4: Confirmatory Multiseed
    final_config = stage_3_base.copy()
    final_config.update(best_3["config"])
    final_config["seeds"] = 32
    
    print("\n--- Starting Stage 4: Confirmatory Multiseed ---")
    stage_4_dir = campaign_dir / "stage_4_confirmatory"
    stage_4_dir.mkdir(parents=True, exist_ok=True)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(run_seed, seed, final_config, stage_4_dir / f"seed_{seed}"): seed for seed in range(32)}
        for future in concurrent.futures.as_completed(futures):
            pass
            
    subprocess.run(["python", str(ENGINE_DIR / "scripts/analyze_outputs.py"), str(stage_4_dir.absolute())], check=True)

    # Save best config
    with open(campaign_dir / "phase_1b_best_config.json", "w") as f:
        json.dump(final_config, f, indent=2)

    # Final reports
    sweep_results = {
        "stage_1": results_1,
        "stage_2": results_2,
        "stage_3": results_3
    }
    with open(campaign_dir / "phase_1b_parameter_sweep_results.json", "w") as f:
        json.dump(sweep_results, f, indent=2)

    # Run Falsification
    print("\n--- Running Falsification Vectors ---")
    subprocess.run(["python", str(ENGINE_DIR / "scripts/falsification_harness.py")], check=True)

    print("\nPhase 1B Campaign Complete.")

if __name__ == "__main__":
    main()
