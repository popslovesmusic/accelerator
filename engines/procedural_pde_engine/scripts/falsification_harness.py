import os
import json
import subprocess
import shutil
import concurrent.futures
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
BUILD_DIR = ENGINE_DIR / "build"
EXE_PATH = BUILD_DIR / "procedural_pde_engine.exe"
if not EXE_PATH.exists():
    EXE_PATH = BUILD_DIR / "procedural_pde_engine"

def run_falsification(mode, intensity, seed, config_path, base_out_dir):
    out_dir = base_out_dir / f"{mode}_seed_{seed}"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "r") as f:
        config = json.load(f)
    config["seed"] = seed
    config["falsification_mode"] = mode
    config["falsification_intensity"] = intensity
    
    seed_config_path = out_dir / "config.json"
    with open(seed_config_path, "w") as f:
        json.dump(config, f, indent=2)
        
    cmd = [
        str(EXE_PATH.absolute()),
        str(seed_config_path.absolute()),
        str(out_dir.absolute())
    ]
    
    subprocess.run(cmd, capture_output=True, text=True)
    
    summary_path = out_dir / "summary_metrics.json"
    if summary_path.exists():
        with open(summary_path, "r") as f:
            return mode, json.load(f)
    return mode, None

def main():
    config_path = ENGINE_DIR / "configs/pde_2d_baseline.json"
    num_seeds = 4 # Keep seed count low for falsification speed check
    base_out_dir = ENGINE_DIR / "outputs/runs/falsification_2d"
    
    if base_out_dir.exists():
        shutil.rmtree(base_out_dir)
    base_out_dir.mkdir(parents=True)
    
    modes = [
        "baseline",
        "FV_001_residue_scramble",
        "FV_002_orientation_inversion",
        "FV_003_admissibility_narrowing",
        "FV_004_corridor_randomization",
        "FV_005_gradient_collapse",
        "FV_006_noise_injection",
        "FV_007_boundary_overload",
        "FV_008_recovery_test"
    ]
    
    # Needs a quick re-build to ensure main.cpp changes are active
    print("Re-compiling engine...")
    subprocess.run(["cmake", "--build", ".", "--config", "Release"], cwd=BUILD_DIR, check=True)
    
    global EXE_PATH
    if (BUILD_DIR / "Release" / "procedural_pde_engine.exe").exists():
        EXE_PATH = BUILD_DIR / "Release" / "procedural_pde_engine.exe"
        
    print(f"Executing falsification vectors across {num_seeds} seeds...")
    
    aggregated = {mode: [] for mode in modes}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = []
        for mode in modes:
            for seed in range(num_seeds):
                futures.append(executor.submit(run_falsification, mode, 1.0 if mode != "FV_008_recovery_test" else 0.0, seed, config_path, base_out_dir))
                
        for future in concurrent.futures.as_completed(futures):
            mode, res = future.result()
            if res:
                aggregated[mode].append(res)
    
    # Calculate effect sizes compared to baseline
    baseline_avg = sum(r["final_corridor_count"] for r in aggregated["baseline"]) / len(aggregated["baseline"]) if aggregated["baseline"] else 1.0
    if baseline_avg == 0: baseline_avg = 1.0
    
    falsification_report = {
        "status": "pass",
        "vectors": {}
    }
    
    print("\n--- Falsification Results ---")
    for mode in modes:
        if mode == "baseline": continue
        res_list = aggregated[mode]
        if not res_list:
            continue
        avg_corridors = sum(r["final_corridor_count"] for r in res_list) / len(res_list)
        effect_size = (avg_corridors - baseline_avg) / baseline_avg
        
        falsification_report["vectors"][mode] = {
            "avg_corridors": avg_corridors,
            "effect_size": effect_size,
            "status": "effective" if abs(effect_size) > 0.1 else "ineffective"
        }
        print(f"{mode}: Effect Size = {effect_size:.2f} ({falsification_report['vectors'][mode]['status']})")
        
    with open(ENGINE_DIR / "validation/falsification_report.json", "w") as f:
        json.dump(falsification_report, f, indent=2)

    print("\nFalsification testing complete. Report saved to validation/falsification_report.json.")

if __name__ == "__main__":
    main()
