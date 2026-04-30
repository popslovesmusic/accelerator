import os
import json
import argparse
import numpy as np
import pandas as pd
import time
from analog_engine import AnalogEngine

def run_simulation(config_path, output_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    
    n_nodes = config.get('n_nodes', 10000)
    steps = config.get('steps', 1000)
    iterations = config.get('iterations', 30)
    dt = config.get('dt', 1.0 / 48000.0)
    
    engine = AnalogEngine(n_nodes)
    
    # Initialize gains matching the C++ benchmark
    engine.feedback_gain = np.array([0.05 * (i % 10) for i in range(n_nodes)])
    
    start_time = time.time()
    for s in range(steps):
        input_val = np.sin(s * 0.01)
        control_val = np.cos(s * 0.01)
        engine.step(input_val, control_val, 0.0, dt, iterations)
    end_time = time.time()
    
    metrics = engine.get_metrics()
    metrics["runtime_ms"] = (end_time - start_time) * 1000.0
    
    summary = {
        "config": config,
        "final_metrics": metrics,
        "run_date": "2026-04-29",
        "status": "completed"
    }
    
    with open(os.path.join(output_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
        
    print(f"Simulation complete. Outputs saved to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="D-ASE Analog Comparison Simulation")
    parser.add_argument("--config", type=str, required=True, help="Path to config JSON")
    parser.add_argument("--out", type=str, required=True, help="Output directory")
    args = parser.parse_args()
    
    run_simulation(args.config, args.out)
