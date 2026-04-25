import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from dynamics import SwarmDynamics

def run_density_trial(n_agents, config):
    # Update config for this trial
    trial_config = config.copy()
    trial_config['n_agents'] = n_agents
    
    dynamics = SwarmDynamics(trial_config)
    
    # Initialize state: x, p, phi, residue, mismatch
    state = np.zeros((5, n_agents))
    state[0] = np.random.normal(0, 0.5, n_agents) # x
    state[1] = np.random.normal(0, 0.5, n_agents) # p
    state[2] = np.random.uniform(0, 2 * np.pi, n_agents) # phi
    state[3] = 0.0 # residue
    state[4] = 0.0 # mismatch
    
    history = []
    dt = trial_config['dt']
    steps = trial_config['steps']
    
    # Run simulation
    for step in range(steps):
        state = dynamics.step_rk4(state, dt)
        
        # Collect metrics in the second half of the simulation to ensure stabilization
        if step > steps // 2 and step % 10 == 0:
            metrics = dynamics.compute_metrics(state)
            history.append(metrics)
            
    df = pd.DataFrame(history)
    
    # Summary metrics for this density
    return {
        "n_agents": n_agents,
        "order_parameter_mean": df['order_parameter'].mean(),
        "order_parameter_std": df['order_parameter'].std(),
        "residue_mean": df['residue_mean'].mean(),
        "local_coherence_mean": df['local_coherence_mean'].mean(),
        "mismatch_mean": df['mismatch_mean'].mean()
    }

def main():
    # Load base config
    base_config = {
        "dt": 0.05,
        "steps": 2000,
        "kappa": 1.0,
        "R_c": 1.5,
        "K_phi": 0.5, # Reduced coupling to see transition
        "omega_mean": 1.0,
        "omega_std": 0.2, # More noise to challenge stability
        "mismatch_rate": 0.05,
        "residue_decay": 0.01,
        "seed": 42
    }
    
    densities = np.arange(1, 51, 1)
    results = []
    
    print(f"Starting density sweep across {len(densities)} points...")
    
    for n in densities:
        print(f"Running n_agents = {n}...")
        res = run_density_trial(n, base_config)
        results.append(res)
        
    df_results = pd.DataFrame(results)
    
    # Output
    out_dir = Path("research_density_stability/outputs/density_sweep")
    out_dir.mkdir(parents=True, exist_ok=True)
    df_results.to_csv(out_dir / "results.csv", index=False)
    
    # Plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Number of Agents (Density Proxy)')
    ax1.set_ylabel('Mean Residue', color=color)
    ax1.plot(df_results['n_agents'], df_results['residue_mean'], marker='o', color=color, label='Residue Mean')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Order Parameter Std Dev', color=color)
    ax2.plot(df_results['n_agents'], df_results['order_parameter_std'], marker='s', color=color, label='Order Param Std')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Regime Transition: Density-Driven Stabilization')
    fig.tight_layout()
    plt.grid(True, alpha=0.3)
    plt.savefig(out_dir / "density_transition_plot.png")
    
    print(f"Results saved to {out_dir}")

if __name__ == "__main__":
    main()
