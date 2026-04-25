import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Reuse the core logic from structural_box_sim_v2/sim.py
def laplacian_neumann_1d(field, dx):
    padded = np.pad(field, (1, 1), mode="edge")
    return (padded[:-2] - 2.0 * field + padded[2:]) / (dx * dx)

def step_fields(epsilon, rho, residue, a, config):
    m = config['model']
    g = config['grid']
    
    epsilon_rhs = (
        m['D_epsilon'] * laplacian_neumann_1d(epsilon, g['dx'])
        + a * epsilon
        - m['b'] * epsilon * rho
        - m['c'] * epsilon * epsilon
        + m['u'] * residue
        + m['s']
    )
    rho_rhs = (
        m['D_rho'] * laplacian_neumann_1d(rho, g['dx'])
        + m['alpha'] * rho
        - m['beta'] * epsilon * rho
        - m['gamma'] * rho * rho
        - m['v'] * residue
        + m['h']
    )
    residue_rhs = (
        m['D_R'] * laplacian_neumann_1d(residue, g['dx'])
        + m['kappa'] * epsilon
        - m['lambda_R'] * residue
    )
    
    next_epsilon = epsilon + g['dt'] * epsilon_rhs
    next_rho = rho + g['dt'] * rho_rhs
    next_residue = residue + g['dt'] * residue_rhs
    
    if m.get('clamp_nonnegative', True):
        next_epsilon = np.maximum(next_epsilon, 0.0)
        next_rho = np.maximum(next_rho, 0.0)
        next_residue = np.maximum(next_residue, 0.0)
        
    return next_epsilon, next_rho, next_residue

def run_experiment(name, initial_residue, a_ramp, config):
    g = config['grid']
    nx = g['nx']
    
    # Initialize
    epsilon = np.zeros(nx)
    # Start with a small bump to trigger activity
    xx = np.linspace(-0.5, 0.5, nx)
    epsilon = 0.4 * np.exp(-0.5 * xx**2 / 0.01)
    
    rho = np.full(nx, 0.3)
    residue = np.full(nx, initial_residue)
    
    history = []
    
    step_count = len(a_ramp)
    for i in range(step_count):
        a = a_ramp[i]
        epsilon, rho, residue = step_fields(epsilon, rho, residue, a, config)
        
        if i % 100 == 0:
            history.append({
                "step": i,
                "time": i * g['dt'],
                "a": a,
                "epsilon_mean": np.mean(epsilon),
                "residue_mean": np.mean(residue)
            })
            
    return pd.DataFrame(history)

def main():
    # Load base config
    config_path = Path("research_residue_hysteresis/box_config_strong_feedback.json")
    with open(config_path, 'r') as f:
        base_config = json.load(f)
    
    # Pre-calculate dx
    base_config['grid']['dx'] = base_config['grid']['length'] / base_config['grid']['nx']
    
    # Define the ramp: Start moderate, ramp to negative growth
    dt = base_config['grid']['dt']
    total_steps = int(30.0 / dt)
    time = np.linspace(0, 30, total_steps)
    
    # Ramp 'a' from 0.5 down to -0.2
    a_ramp = np.linspace(0.5, -0.2, total_steps)
    
    print("Running Trial 1: Low Initial Residue (Control)...")
    df_control = run_experiment("Control", 0.0, a_ramp, base_config)
    
    print("Running Trial 2: High Initial Residue (Test)...")
    # 1.5 is a high residue level
    df_test = run_experiment("Test", 1.5, a_ramp, base_config)
    
    # Save results
    out_dir = Path("research_residue_hysteresis/outputs/hysteresis_v3")
    out_dir.mkdir(parents=True, exist_ok=True)
    df_control.to_csv(out_dir / "control.csv", index=False)
    df_test.to_csv(out_dir / "test.csv", index=False)
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(df_control['a'], df_control['epsilon_mean'], label='Control (R_init=0.0)')
    plt.plot(df_test['a'], df_test['epsilon_mean'], label='Test (R_init=1.5)')
    plt.gca().invert_xaxis() # Show ramp from 0.8 to 0.2
    plt.xlabel('Growth Parameter (a)')
    plt.ylabel('Mean Mismatch (epsilon)')
    plt.title('Hysteresis: Epsilon Persistence via Residue')
    plt.legend()
    plt.grid(True)
    plt.savefig(out_dir / "hysteresis_plot.png")
    
    print(f"Results saved to {out_dir}")

if __name__ == "__main__":
    main()
