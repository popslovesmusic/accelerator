import os
import json
import argparse
import numpy as np
import time
from field_engine import SATPHiggsEngine2D

def run_simulation(config_path, output_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    
    nx = config.get('size', 128)
    ny = nx
    steps = config.get('steps', 500)
    dt = config.get('dt', 0.001)
    dx = config.get('dx', 0.01)
    
    h_vev = config.get('h_vev', 1.0)
    lambda_h = config.get('lambda_h', 0.1)
    g = config.get('g', 0.01)
    
    engine = SATPHiggsEngine2D(nx, ny)
    engine.initialize_vacuum(h_vev)
    
    # Gaussian bump perturbation in phi matching C++ benchmark
    mid_x, mid_y = nx // 2, ny // 2
    sigma = 0.05 * (nx * dx)
    y, x = np.ogrid[:ny, :nx]
    r2 = (x*dx - mid_x*dx)**2 + (y*dx - mid_y*dx)**2
    engine.phi[:] = 0.5 * np.exp(-r2 / (2.0 * sigma**2))
    engine.phi_prev[:] = engine.phi[:]
    
    start_time = time.time()
    for _ in range(steps):
        engine.step(dt, dx, h_vev, lambda_h, g)
    end_time = time.time()
    
    metrics = engine.get_metrics(h_vev)
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
    parser = argparse.ArgumentParser(description="SATP+Higgs 2D Comparison Simulation")
    parser.add_argument("--config", type=str, required=True, help="Path to config JSON")
    parser.add_argument("--out", type=str, required=True, help="Output directory")
    args = parser.parse_args()
    
    run_simulation(args.config, args.out)
