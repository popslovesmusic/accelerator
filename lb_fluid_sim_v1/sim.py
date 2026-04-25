import os
import json
import argparse
import numpy as np
import pandas as pd
from lb_engine import LBEngine

def run_simulation(config_path, output_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(config.get('seed', 42))
    
    engine = LBEngine(config)
    
    history = []
    steps = config['steps']
    
    print(f"Starting LBM simulation on {config['nx']}x{config['ny']} grid for {steps} steps...")
    
    for step in range(steps):
        engine.evolve()
        
        if step % 50 == 0:
            metrics = engine.get_metrics()
            metrics['step'] = step
            history.append(metrics)
            
            if step % 200 == 0:
                print(f"Step {step}: Fluid Volume = {metrics['fluid_volume']:.0f}, Mean Velocity = {metrics['mean_velocity']:.4f}")

        # Optional: Save snapshots
        if step in [0, steps // 4, steps // 2, 3 * steps // 4, steps - 1]:
            save_snapshot(engine, step, output_dir)

    # Save metrics
    df = pd.DataFrame(history)
    df.to_csv(os.path.join(output_dir, 'metrics.csv'), index=False)
    
    # Save final summary
    summary = {
        "config": config,
        "final_metrics": history[-1],
        "status": "completed"
    }
    with open(os.path.join(output_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
        
    print(f"Simulation complete. Outputs saved to {output_dir}")

def save_snapshot(engine, step, output_dir):
    try:
        import matplotlib.pyplot as plt
        snapshot_dir = os.path.join(output_dir, 'snapshots')
        os.makedirs(snapshot_dir, exist_ok=True)
        
        velocity = np.sqrt(engine.ux**2 + engine.uy**2)
        velocity[engine.boundaries] = np.nan # Mask walls
        
        plt.figure(figsize=(12, 5))
        plt.imshow(velocity, cmap='jet', origin='lower')
        plt.colorbar(label='Velocity Magnitude')
        # Overlay boundaries
        plt.contour(engine.boundaries, levels=[0.5], colors='white', linewidths=1)
        plt.title(f'Fluid Flow and Boundaries (Step {step})')
        plt.savefig(os.path.join(snapshot_dir, f'snapshot_step_{step:04d}.png'))
        plt.close()
    except ImportError:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lattice Boltzmann Fluid-like Simulation")
    parser.add_argument("--config", type=str, default="configs/default.json", help="Path to config JSON")
    parser.add_argument("--out", type=str, default="outputs/default_run", help="Output directory")
    args = parser.parse_args()
    
    run_simulation(args.config, args.out)
