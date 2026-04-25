import os
import json
import argparse
import numpy as np
import pandas as pd
from fsa_engine import RuleEngine, FSAAgent

def run_simulation(config_path, output_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(config.get('seed', 42))
    
    engine = RuleEngine(config)
    n_agents = config['n_agents']
    steps = config['steps']
    
    # Initialize agents starting at node 1
    agents = [FSAAgent(start_node=1) for _ in range(n_agents)]
    
    history = []
    
    print(f"Starting Rule Engine simulation with {n_agents} agents for {steps} steps...")
    
    for step in range(steps):
        # Step every agent
        for agent in agents:
            agent.step(engine)
            
        # Compute metrics
        active_agents = [a for agent in agents if (a := agent).active]
        n_active = len(active_agents)
        avg_res = np.mean([a.residue for a in active_agents]) if n_active > 0 else 0
        
        metrics = {
            "step": step,
            "active_count": n_active,
            "mean_residue": float(avg_res)
        }
        history.append(metrics)
        
        if step % 20 == 0:
            print(f"Step {step}: Active Agents = {n_active}, Mean Residue = {avg_res:.2f}")

    # Save metrics
    df = pd.DataFrame(history)
    df.to_csv(os.path.join(output_dir, 'metrics.csv'), index=False)
    
    # Final state distribution
    final_states = [a.current_state for a in agents if a.active]
    state_counts = pd.Series(final_states).value_counts().to_dict()
    
    # Save final summary
    summary = {
        "config": config,
        "final_metrics": history[-1],
        "state_distribution": {str(k): int(v) for k, v in state_counts.items()},
        "total_halted": n_agents - len(active_agents),
        "status": "completed"
    }
    with open(os.path.join(output_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
        
    print(f"Simulation complete. Outputs saved to {output_dir}")

    # Optional Plotting
    plot_results(engine, agents, output_dir)

def plot_results(engine, agents, output_dir):
    try:
        import networkx as nx
        import matplotlib.pyplot as plt
        
        plots_dir = os.path.join(output_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # 1. State Graph Visualization
        G = engine.G
        pos = nx.spring_layout(G, seed=42)
        
        # Color nodes by agent population
        active_states = [a.current_state for a in agents if a.active]
        pop = {n: 0 for n in G.nodes()}
        for s in active_states:
            pop[s] += 1
            
        node_colors = [pop[n] for n in G.nodes()]
        
        plt.figure(figsize=(10, 8))
        nx.draw_networkx_nodes(G, pos, node_size=200, node_color=node_colors, cmap='viridis', alpha=0.8)
        nx.draw_networkx_edges(G, pos, alpha=0.3, arrows=True)
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        # Highlight Forbidden Node
        nx.draw_networkx_nodes(G, pos, nodelist=[engine.forbidden], node_color='red', node_size=300, label='Forbidden (L0)')
        
        plt.title("State Graph and Agent Distribution")
        plt.legend()
        plt.savefig(os.path.join(plots_dir, 'state_graph.png'))
        plt.close()
        
    except ImportError as e:
        print(f"Plotting dependencies missing: {e}. Skipping plots.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Finite-State Automata / Rule Engine Simulation")
    parser.add_argument("--config", type=str, default="configs/default.json", help="Path to config JSON")
    parser.add_argument("--out", type=str, default="outputs/default_run", help="Output directory")
    args = parser.parse_args()
    
    run_simulation(args.config, args.out)
