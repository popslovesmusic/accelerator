import os
import json
import argparse
import numpy as np
import pandas as pd
from sde_engine import StochasticEngine

def run_simulation(config_path, output_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(config.get('seed', 42))
    
    engine = StochasticEngine(config)
    
    history = []
    dt = config['dt']
    steps = config['steps']
    
    # Optional: store a few trajectories for plotting
    trace_indices = np.random.choice(config['n_particles'], min(5, config['n_particles']), replace=False)
    traces = []

    print(f"Starting stochastic simulation with {config['n_particles']} particles for {steps} steps...")
    
    for step in range(steps):
        t = step * dt
        has_crossed = engine.step(t)
        
        # Log metrics
        if step % 10 == 0:
            metrics = engine.get_metrics()
            metrics['step'] = step
            metrics['time'] = t
            history.append(metrics)
            
            if step % 500 == 0:
                print(f"Step {step}: Crossing Fraction = {metrics['crossing_fraction']:.4f}, Mean X = {metrics['mean_x']:.4f}")

        # Store traces
        traces.append(engine.x[trace_indices].copy())

    # Save metrics
    df = pd.DataFrame(history)
    df.to_csv(os.path.join(output_dir, 'metrics.csv'), index=False)
    
    # Save final summary
    valid_onsets = engine.onset_times[engine.has_crossed]
    summary = {
        "config": config,
        "final_metrics": history[-1],
        "onset_stats": {
            "mean_onset_time": float(np.mean(valid_onsets)) if len(valid_onsets) > 0 else None,
            "min_onset_time": float(np.min(valid_onsets)) if len(valid_onsets) > 0 else None,
            "total_onsets": len(valid_onsets)
        },
        "status": "completed"
    }
    with open(os.path.join(output_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
        
    print(f"Simulation complete. Outputs saved to {output_dir}")

    # Optional Plotting
    plot_results(df, np.array(traces), valid_onsets, config, output_dir)

def plot_results(df, traces_arr, onset_times, config, output_dir):
    try:
        import matplotlib.pyplot as plt
        plots_dir = os.path.join(output_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        time_axis = np.arange(traces_arr.shape[0]) * config['dt']
        
        # 1. Trajectory Traces
        plt.figure(figsize=(10, 5))
        for i in range(traces_arr.shape[1]):
            plt.plot(time_axis, traces_arr[:, i], alpha=0.7)
        plt.axhline(config['x_thresh'], color='red', linestyle='--', label='Threshold')
        plt.xlabel('Time')
        plt.ylabel('Position (x)')
        plt.title('Stochastic Trajectory Samples')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(plots_dir, 'trajectories.png'))
        plt.close()
        
        # 2. Onset Time Histogram
        if len(onset_times) > 0:
            plt.figure(figsize=(10, 5))
            plt.hist(onset_times, bins=30, color='skyblue', edgecolor='black')
            plt.xlabel('Onset Time')
            plt.ylabel('Frequency')
            plt.title('Distribution of Phase Packet Onset Times')
            plt.grid(True, axis='y')
            plt.savefig(os.path.join(plots_dir, 'onset_histogram.png'))
            plt.close()
            
    except ImportError:
        print("Matplotlib not found. Skipping plots.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stochastic Threshold Simulation")
    parser.add_argument("--config", type=str, default="configs/default.json", help="Path to config JSON")
    parser.add_argument("--out", type=str, default="outputs/default_run", help="Output directory")
    args = parser.parse_args()
    
    run_simulation(args.config, args.out)
