import argparse
import json
import os
import time
from pathlib import Path
from agent_cpp_wrapper import AgentEngineCPP

def run_sim(config_path, out_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)

    agent_count = config.get("agent_count", 10000)
    steps = config.get("steps", 100)
    dt = config.get("dt", 0.01)
    
    # Swarm parameters
    kappa = config.get("kappa", 1.0)
    R_c = config.get("R_c", 0.5)
    K_phi = config.get("K_phi", 1.0)
    mismatch_rate = config.get("mismatch_rate", 0.01)
    residue_decay = config.get("residue_decay", 0.1)
    
    # Init parameters
    seed = config.get("seed", 42)
    x_std = config.get("x_std", 0.5)
    p_std = config.get("p_std", 0.5)
    omega_mean = config.get("omega_mean", 1.0)
    omega_std = config.get("omega_std", 0.1)

    print(f"Initializing AgentEngineCPP with {agent_count} agents...")
    engine = AgentEngineCPP(agent_count)
    engine.set_params(kappa, R_c, K_phi, mismatch_rate, residue_decay)
    engine.initialize(seed, x_std, p_std, omega_mean, omega_std)

    print(f"Running simulation for {steps} steps...")
    start_time = time.time()
    for i in range(steps):
        engine.step(dt)
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
