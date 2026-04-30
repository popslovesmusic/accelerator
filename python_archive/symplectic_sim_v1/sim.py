import os
import json
import argparse
import numpy as np
import pandas as pd
from symplectic_engine import HamiltonianEngine

def run_simulation(config_path, output_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(config.get('seed', 42))
    
    engine = HamiltonianEngine(config)
    steps = config['steps']
    
    history = []
    # Save traces for a subset of particles for plotting
    trace_indices = [0, 1, 2, 3, 4]
    traces = {idx: {"q": [], "p": []} for idx in trace_indices}

    print(f"Starting symplectic simulation with {config['n_particles']} particles for {steps} steps...")
    
    for step in range(steps):
        engine.step_leapfrog()
        
        if step % 20 == 0:
            metrics = engine.get_metrics()
            metrics['step'] = step
            history.append(metrics)
            
            for idx in trace_indices:
                traces[idx]["q"].append(engine.q[idx])
                traces[idx]["p"].append(engine.p[idx])
            
            if step % 1000 == 0:
                print(f"Step {step}: Mean H = {metrics['mean_H']:.6f}, Energy spread = {metrics['std_H']:.6f}")

    # Save metrics
    df = pd.DataFrame(history)
    df.to_csv(os.path.join(output_dir, 'metrics.csv'), index=False)
    
    # Save final summary
    summary = {
        "config": config,
        "final_metrics": history[-1],
        "energy_drift": float(df['mean_H'].iloc[-1] - df['mean_H'].iloc[0]),
        "status": "completed"
    }
    with open(os.path.join(output_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
        
    print(f"Simulation complete. Outputs saved to {output_dir}")

    # Optional Plotting
    plot_results(df, traces, output_dir)

def plot_results(df, traces, output_dir):
    try:
        import matplotlib.pyplot as plt
        plots_dir = os.path.join(output_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # 1. Energy Conservation
        plt.figure(figsize=(10, 5))
        plt.plot(df['step'], df['mean_H'], label='Mean Hamiltonian (Energy)')
        plt.xlabel('Step')
        plt.ylabel('H')
        plt.title('Energy Conservation (Symplectic Integration)')
        plt.grid(True)
        plt.savefig(os.path.join(plots_dir, 'energy_conservation.png'))
        plt.close()
        
        # 2. Phase-Space Traces
        plt.figure(figsize=(8, 8))
        for idx, trace in traces.items():
            plt.plot(trace["q"], trace["p"], alpha=0.6, label=f'Particle {idx}')
        plt.xlabel('Position (q)')
        plt.ylabel('Momentum (p)')
        plt.title('Phase-Space Orbits (Nonlinear Pendulum)')
        plt.grid(True)
        plt.axhline(0, color='black', alpha=0.3)
        plt.axvline(0, color='black', alpha=0.3)
        plt.savefig(os.path.join(plots_dir, 'phase_space.png'))
        plt.close()
        
    except ImportError:
        print("Matplotlib not found. Skipping plots.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hamiltonian / Symplectic Simulation")
    parser.add_argument("--config", type=str, default="configs/default.json", help="Path to config JSON")
    parser.add_argument("--out", type=str, default="outputs/default_run", help="Output directory")
    args = parser.parse_args()
    
    run_simulation(args.config, args.out)
