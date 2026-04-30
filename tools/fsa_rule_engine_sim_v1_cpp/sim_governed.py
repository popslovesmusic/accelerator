import argparse
import json
import os
import time
from pathlib import Path
from fsa_cpp_wrapper import FSAEngineCPP

def run_sim(config_path, out_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)

    num_agents = config.get("num_agents", 1000)
    n_states = config.get("n_states", 10)
    forbidden = config.get("forbidden", 9)
    res_thresh = config.get("res_thresh", 5)
    res_req = config.get("res_req", 2)
    steps = config.get("steps", 100)
    
    # Init parameters
    start_node = config.get("start_node", 0)
    seed = config.get("seed", 42)

    print(f"Initializing FSAEngineCPP with {num_agents} agents and {n_states} states...")
    engine = FSAEngineCPP(num_agents, n_states, forbidden, res_thresh, res_req)
    engine.initialize(start_node, seed)

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
