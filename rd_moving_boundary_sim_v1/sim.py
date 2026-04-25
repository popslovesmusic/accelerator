import os
import json
import argparse
import numpy as np
import pandas as pd
from rd_engine import RDEngine

def run_simulation(config_path, output_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(config.get('seed', 42))
    
    engine = RDEngine(config)
    
    history = []
    steps = config['steps']
    
    print(f"Starting Reaction-Diffusion simulation on {config['grid_size']}x{config['grid_size']} grid...")
    
    for step in range(steps):
        engine.step()
        
        if step % 10 == 0:
            metrics = engine.get_metrics()
            metrics['step'] = step
            history.append(metrics)
            
            if step % 200 == 0:
                print(f"Step {step}: Active Area = {metrics['active_area']:.2f}, Total Signal = {metrics['total_signal']:.2f}")

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
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        im1 = axes[0].imshow(engine.D, cmap='Blues', vmin=0, vmax=1)
        axes[0].set_title(f'Domain D (Step {step})')
        fig.colorbar(im1, ax=axes[0])
        
        im2 = axes[1].imshow(engine.S, cmap='hot')
        axes[1].set_title(f'Signal S (Step {step})')
        fig.colorbar(im2, ax=axes[1])
        
        plt.savefig(os.path.join(snapshot_dir, f'snapshot_step_{step:04d}.png'))
        plt.close()
    except ImportError:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reaction-Diffusion Moving Boundary Simulation")
    parser.add_argument("--config", type=str, default="configs/default.json", help="Path to config JSON")
    parser.add_argument("--out", type=str, default="outputs/default_run", help="Output directory")
    args = parser.parse_args()
    
    run_simulation(args.config, args.out)
