import os
import json
import argparse
import numpy as np
import pandas as pd
from kuramoto_engine import KuramotoEngine

def run_simulation(config_path, output_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(config.get('seed', 42))
    
    engine = KuramotoEngine(config)
    n = config['n_oscillators']
    phi = np.random.uniform(0, 2 * np.pi, size=n)
    
    history = []
    dt = config['dt']
    steps = config['steps']
    
    # For spatiotemporal visualization
    phase_history = []
    
    print(f"Starting Kuramoto simulation with {n} oscillators for {steps} steps...")
    
    for step in range(steps):
        phi = engine.step_rk4(phi, dt)
        
        if step % 10 == 0:
            metrics = engine.compute_metrics(phi)
            metrics['step'] = step
            metrics['time'] = step * dt
            history.append(metrics)
            phase_history.append(phi.copy())
            
            if step % 500 == 0:
                print(f"Step {step}: Global R = {metrics['order_parameter']:.4f}, Local Coherence = {metrics['local_coherence_mean']:.4f}")

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
    plot_results(df, np.array(phase_history), output_dir)

def plot_results(df, phases_st, output_dir):
    try:
        import matplotlib.pyplot as plt
        plots_dir = os.path.join(output_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # 1. Hovmöller Diagram (Spatiotemporal Phase)
        plt.figure(figsize=(10, 8))
        plt.imshow(phases_st, aspect='auto', cmap='hsv', origin='lower',
                   extent=[0, phases_st.shape[1], 0, df['time'].iloc[-1]])
        plt.colorbar(label='Phase (rad)')
        plt.xlabel('Oscillator Index')
        plt.ylabel('Time')
        plt.title('Spatiotemporal Phase Evolution')
        plt.savefig(os.path.join(plots_dir, 'phase_evolution.png'))
        plt.close()
        
        # 2. Global Order Parameter Evolution
        plt.figure(figsize=(10, 5))
        plt.plot(df['time'], df['order_parameter'], label='Global Order Parameter (R)')
        plt.plot(df['time'], df['local_coherence_mean'], label='Local Coherence Mean')
        plt.xlabel('Time')
        plt.ylabel('Coherence')
        plt.title('Synchronization Evolution')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(plots_dir, 'coherence.png'))
        plt.close()
        
    except ImportError:
        print("Matplotlib not found. Skipping plots.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kuramoto Oscillator Network Simulation")
    parser.add_argument("--config", type=str, default="configs/default.json", help="Path to config JSON")
    parser.add_argument("--out", type=str, default="outputs/default_run", help="Output directory")
    args = parser.parse_args()
    
    run_simulation(args.config, args.out)
