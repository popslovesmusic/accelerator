import argparse
import json
import os
import time
from pathlib import Path
from ca_cpp_wrapper import CAEngineCPP

def run_sim(config_path, out_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)

    width = config.get("width", 256)
    height = config.get("height", 256)
    steps = config.get("steps", 100)
    
    # CA parameters
    D = config.get("D", 0.1)
    delta_R = config.get("delta_R", 0.01)
    gamma_R = config.get("gamma_R", 0.01)
    
    # Init parameters
    source_strength = config.get("source_strength", 1.0)
    source_radius = config.get("source_radius", 5)
    initial_residue = config.get("initial_residue", 0.0)

    print(f"Initializing CAEngineCPP with {width}x{height} grid...")
    engine = CAEngineCPP(width, height)
    engine.set_params(D, delta_R, gamma_R)
    engine.initialize(source_strength, source_radius, initial_residue)

    print(f"Running simulation for {steps} steps...")
    start_time = time.time()
    for i in range(steps):
        engine.step()
    end_time = time.time()
    
    runtime_ms = (end_time - start_time) * 1000
    final_metrics = engine.get_metrics()
    final_metrics["runtime_ms"] = runtime_ms

    output = {
        "config": config,
        "final_metrics": final_metrics
    }

    os.makedirs(out_dir, exist_ok=True)
    out_path = Path(out_dir) / "summary.json"
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=4)
    
    print(f"Simulation complete. Summary saved to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()
    
    run_sim(args.config, args.out)
