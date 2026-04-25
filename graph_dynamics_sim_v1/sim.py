import os
import json
import argparse
import numpy as np
import pandas as pd
from network_engine import NetworkDynamics

def run_simulation(config_path, output_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(config.get('seed', 42))
    
    n = config['n_nodes']
    # Initialize phases uniformly [0, 2pi]
    phi = np.random.uniform(0, 2 * np.pi, n)
    
    net = NetworkDynamics(config)
    
    history = []
    dt = config['dt']
    steps = config['steps']
    
    print(f"Starting network dynamics simulation with {n} nodes for {steps} steps...")
    
    for step in range(steps):
        # 1. Update node states (phases)
        phi = net.step_phi(phi, dt)
        
        # 2. Rewire topology based on new states
        net.rewire(phi)
        
        if step % 10 == 0:
            metrics = net.get_metrics(phi)
            metrics['step'] = step
            metrics['time'] = step * dt
            history.append(metrics)
            
            if step % 100 == 0:
                print(f"Step {step}: Order Param = {metrics['order_parameter']:.4f}, Edges = {metrics['edge_count']}")

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
    plot_network(net, phi, output_dir)

def plot_network(net, phi, output_dir):
    try:
        import networkx as nx
        import matplotlib.pyplot as plt
        
        plots_dir = os.path.join(output_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        G = nx.from_numpy_array(net.A)
        pos = nx.spring_layout(G, seed=42)
        
        plt.figure(figsize=(10, 10))
        nx.draw_networkx_nodes(G, pos, node_size=100, node_color=phi, cmap='hsv', alpha=0.8)
        nx.draw_networkx_edges(G, pos, alpha=0.2)
        plt.title("Final Network Topology and Node Phases")
        plt.savefig(os.path.join(plots_dir, 'final_network.png'))
        plt.close()
        
        # Plot Edge Count Evolution
        metrics_df = pd.read_csv(os.path.join(output_dir, 'metrics.csv'))
        plt.figure(figsize=(10, 5))
        plt.plot(metrics_df['time'], metrics_df['edge_count'], label='Edge Count')
        plt.plot(metrics_df['time'], metrics_df['order_parameter'] * metrics_df['edge_count'].max(), label='Order Param (Scaled)')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        plt.title("Network Evolution over Time")
        plt.grid(True)
        plt.savefig(os.path.join(plots_dir, 'evolution.png'))
        plt.close()
        
    except ImportError as e:
        print(f"Plotting dependencies missing: {e}. Skipping plots.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dynamic Graph / Network Dynamics Simulation")
    parser.add_argument("--config", type=str, default="configs/default.json", help="Path to config JSON")
    parser.add_argument("--out", type=str, default="outputs/default_run", help="Output directory")
    args = parser.parse_args()
    
    run_simulation(args.config, args.out)
