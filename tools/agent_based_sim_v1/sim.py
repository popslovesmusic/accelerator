import os
import json
import argparse
import numpy as np
import pandas as pd
from dynamics import SwarmDynamics

def run_simulation(config_path, output_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(config.get('seed', 42))
    
    n = config['n_agents']
    # Initialize state: x, p, phi, residue, mismatch
    state = np.zeros((5, n))
    
    dist_type = config.get('initial_distribution', 'gaussian')
    if dist_type == 'two_clusters':
        # Two clusters far apart (e.g., at x=-5 and x=+5)
        half = n // 2
        state[0, :half] = np.random.normal(-5, 0.1, half)
        state[0, half:] = np.random.normal(5, 0.1, n - half)
        state[1] = np.random.normal(0, 0.1, n)
        # Give different initial phase ranges to the two clusters
        state[2, :half] = np.random.uniform(0, np.pi, half)
        state[2, half:] = np.random.uniform(np.pi, 2 * np.pi, n - half)
    else:
        # Default: small random cluster
        state[0] = np.random.normal(0, 0.5, n) # x
        state[1] = np.random.normal(0, 0.5, n) # p
        state[2] = np.random.uniform(0, 2 * np.pi, n) # phi
        
    state[3] = 0.0 # residue
    state[4] = 0.0 # mismatch
    
    dynamics = SwarmDynamics(config)
    
    history = []
    dt = config['dt']
    steps = config['steps']
    
    print(f"Starting swarm simulation with {n} agents for {steps} steps...")
    
    for step in range(steps):
        state = dynamics.step_rk4(state, dt)
        
        if step % 10 == 0:
            metrics = dynamics.compute_metrics(state)
            metrics['step'] = step
            metrics['time'] = step * dt
            history.append(metrics)
            
            if step % 100 == 0:
                print(f"Step {step}: Order Parameter = {metrics['order_parameter']:.4f}, Mean Residue = {metrics['residue_mean']:.4f}")

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

    # Optional Plotting
    plot_results(df, state, output_dir)

def plot_results(df, final_state, output_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not found, skipping plots.")
        return

    os.makedirs(os.path.join(output_dir, 'plots'), exist_ok=True)
    
    # 1. Order Parameter over time
    plt.figure(figsize=(10, 5))
    plt.plot(df['time'], df['order_parameter'], label='Order Parameter (Phase Coherence)')
    plt.plot(df['time'], df['residue_mean'], label='Mean Residue')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Swarm Coherence and Residue Evolution')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'plots/evolution.png'))
    plt.close()
    
    # 2. Final Phase-Space
    plt.figure(figsize=(8, 8))
    plt.scatter(final_state[0], final_state[1], c=final_state[2], cmap='hsv', alpha=0.6)
    plt.colorbar(label='Phase (rad)')
    plt.xlabel('Position (x)')
    plt.ylabel('Momentum (p)')
    plt.title('Final Agent Distribution in Phase-Space')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'plots/phase_space.png'))
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent-Based Phase-Space Swarm Simulation")
    parser.add_argument("--config", type=str, default="configs/default.json", help="Path to config JSON")
    parser.add_argument("--out", type=str, default="outputs/default_run", help="Output directory")
    args = parser.parse_args()
    
    run_simulation(args.config, args.out)
