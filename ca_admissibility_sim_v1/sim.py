import os
import json
import argparse
import numpy as np
import pandas as pd
from ca_engine import AdmissibilityCA

def run_simulation(config_path, output_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(config.get('seed', 42))
    
    ca = AdmissibilityCA(config)
    
    history = []
    steps = config['steps']
    
    print(f"Starting CA simulation on {config['grid_size']}x{config['grid_size']} grid for {steps} steps...")
    
    for step in range(steps):
        admissible_mask = ca.step()
        
        if step % 10 == 0:
            metrics = ca.get_metrics(admissible_mask)
            metrics['step'] = step
            history.append(metrics)
            
            if step % 50 == 0:
                print(f"Step {step}: Active Fraction = {metrics['active_fraction']:.4f}, Mean Residue = {metrics['mean_residue']:.4f}")

        # Optional: Save snapshots
        if step in [0, steps // 4, steps // 2, 3 * steps // 4, steps - 1]:
            save_snapshot(ca, step, output_dir)

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

def save_snapshot(ca, step, output_dir):
    try:
        import matplotlib.pyplot as plt
        snapshot_dir = os.path.join(output_dir, 'snapshots')
        os.makedirs(snapshot_dir, exist_ok=True)
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        im1 = axes[0].imshow(ca.epsilon, cmap='viridis')
        axes[0].set_title(f'Mismatch (Step {step})')
        fig.colorbar(im1, ax=axes[0])
        
        im2 = axes[1].imshow(ca.R, cmap='magma')
        axes[1].set_title(f'Residue (Step {step})')
        fig.colorbar(im2, ax=axes[1])
        
        plt.savefig(os.path.join(snapshot_dir, f'snapshot_step_{step:04d}.png'))
        plt.close()
    except ImportError:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cellular Automata Admissibility Simulation")
    parser.add_argument("--config", type=str, default="configs/default.json", help="Path to config JSON")
    parser.add_argument("--out", type=str, default="outputs/default_run", help="Output directory")
    args = parser.parse_args()
    
    run_simulation(args.config, args.out)
