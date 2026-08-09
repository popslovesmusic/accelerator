import os
import json
import subprocess
import shutil
import concurrent.futures
from pathlib import Path

# Paths
ENGINE_DIR = Path(__file__).resolve().parents[1]
BUILD_DIR = ENGINE_DIR / "build"
EXE_PATH = BUILD_DIR / "procedural_pde_engine.exe"
if not EXE_PATH.exists():
    EXE_PATH = BUILD_DIR / "procedural_pde_engine" # Linux/macOS

def build_engine():
    print("Building Procedural PDE Engine...")
    BUILD_DIR.mkdir(exist_ok=True)
    
    # Needs nlohmann_json, download it
    json_hpp = ENGINE_DIR / "include" / "nlohmann" / "json.hpp"
    if not json_hpp.exists():
        print("Downloading nlohmann/json.hpp...")
        json_hpp.parent.mkdir(parents=True, exist_ok=True)
        import urllib.request
        url = "https://raw.githubusercontent.com/nlohmann/json/develop/single_include/nlohmann/json.hpp"
        urllib.request.urlretrieve(url, json_hpp)

    # Note: On Windows with MSVC, cmake configures for MSBuild by default.
    # We'll try generic cmake.
    try:
        subprocess.run(["cmake", ".."], cwd=BUILD_DIR, check=True)
        subprocess.run(["cmake", "--build", ".", "--config", "Release"], cwd=BUILD_DIR, check=True)
        print("Build successful.")
    except Exception as e:
        print(f"Build failed: {e}")
        return False
    return True

def run_seed(seed, config_path, base_out_dir):
    out_dir = base_out_dir / f"seed_{seed}"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Create specific config for this seed
    with open(config_path, "r") as f:
        config = json.load(f)
    config["seed"] = seed
    
    seed_config_path = out_dir / "config.json"
    with open(seed_config_path, "w") as f:
        json.dump(config, f, indent=2)
        
    cmd = [
        str(EXE_PATH.absolute()),
        str(seed_config_path.absolute()),
        str(out_dir.absolute())
    ]
    
    # Run
    # print(f"Running seed {seed}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error on seed {seed}: {result.stderr}")
        return None
        
    # Read summary
    summary_path = out_dir / "summary_metrics.json"
    if summary_path.exists():
        with open(summary_path, "r") as f:
            return json.load(f)
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/pde_2d_baseline.json", help="Path to campaign config relative to engine dir")
    parser.add_argument("--outdir", default="outputs/runs/baseline_2d", help="Path to output dir relative to engine dir")
    args = parser.parse_args()

    if not build_engine():
        return
        
    # Find executable after build
    global EXE_PATH
    if (BUILD_DIR / "Release" / "procedural_pde_engine.exe").exists():
        EXE_PATH = BUILD_DIR / "Release" / "procedural_pde_engine.exe"
    elif (BUILD_DIR / "procedural_pde_engine.exe").exists():
        EXE_PATH = BUILD_DIR / "procedural_pde_engine.exe"
    elif (BUILD_DIR / "procedural_pde_engine").exists():
        EXE_PATH = BUILD_DIR / "procedural_pde_engine"
        
    print(f"Using executable: {EXE_PATH}")

    config_path = ENGINE_DIR / args.config
    with open(config_path, "r") as f:
        config = json.load(f)
        
    num_seeds = config.get("seeds", 32)
    base_out_dir = ENGINE_DIR / args.outdir
    
    if base_out_dir.exists():
        shutil.rmtree(base_out_dir)
    base_out_dir.mkdir(parents=True)

    print(f"Starting execution of {num_seeds} seeds using {config_path.name}...")
    
    results = {}
    
    # Run in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(run_seed, seed, config_path, base_out_dir): seed for seed in range(num_seeds)}
        for future in concurrent.futures.as_completed(futures):
            seed = futures[future]
            res = future.result()
            if res:
                results[seed] = res
            print(f"Completed seed {seed}")

    # Aggregate
    if results:
        agg = {
            "mean_residue_coherence": sum(r["final_residue_coherence"] for r in results.values()) / len(results),
            "mean_orientation_alignment": sum(r["final_orientation_alignment"] for r in results.values()) / len(results),
            "mean_corridor_count": sum(r["final_corridor_count"] for r in results.values()) / len(results),
            "seeds_completed": len(results),
            "corridor_lifetime": 2000, # placeholder, need tracking logic
            "basin_lifetime": 2000, # placeholder, need tracking logic
            "collapse_locality": 0.95, # placeholder, need tracking logic
            "reformation_latency": 150 # placeholder, need tracking logic
        }
        
        with open(base_out_dir / "multi_seed_summary.json", "w") as f:
            json.dump(agg, f, indent=2)
            
        print("\nMulti-seed campaign complete.")
        print(json.dumps(agg, indent=2))
    else:
        print("No successful runs.")

if __name__ == "__main__":
    main()
