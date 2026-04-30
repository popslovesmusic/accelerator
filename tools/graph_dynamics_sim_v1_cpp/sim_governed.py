import argparse
import json
import os
import time
from pathlib import Path
from network_cpp_wrapper import NetworkEngineCPP

def run_sim(config_path, out_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)

    n_nodes = config.get("n_nodes", 100)
    steps = config.get("steps", 100)
    dt = config.get("dt", 0.01)
    
    # Network parameters
    K = config.get("K", 1.0)
    theta_de = config.get("theta_de", 0.1)
    theta_re = config.get("theta_re", 0.1)
    P_re = config.get("P_re", 0.01)
    
    # Init parameters
    seed = config.get("seed", 42)
    omega_mean = config.get("omega_mean", 1.0)
    omega_std = config.get("omega_std", 0.1)

    print(f"Initializing NetworkEngineCPP with {n_nodes} nodes...")
    engine = NetworkEngineCPP(n_nodes)
    engine.set_params(K, theta_de, theta_re, P_re)
    engine.initialize(seed, omega_mean, omega_std)

    print(f"Running simulation for {steps} steps...")
    start_time = time.time()
    for i in range(steps):
        engine.step(dt)
        if i % 10 == 0:
            engine.rewire()
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
