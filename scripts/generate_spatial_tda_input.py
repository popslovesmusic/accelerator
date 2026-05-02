import numpy as np
import os
import json
import sys
from pathlib import Path

# Add tools directory to path
sys.path.append(str(Path(__file__).parent.parent / "tools" / "agent_based_sim_v1"))
from dynamics import SwarmDynamics

def generate_spatial_grid():
    # Use parameters for high coupling
    config = {
        "n_agents": 500,
        "R_c": 1.0,
        "K_phi": 5.0,
        "kappa": 0.5,
        "mismatch_rate": 0.05,
        "residue_decay": 0.1,
        "omega_mean": 1.0,
        "omega_std": 0.1,
        "seed": 42
    }
    
    np.random.seed(config['seed'])
    engine = SwarmDynamics(config)
    
    # Init state: x, p, phi, residue, mismatch
    state = np.zeros((5, config['n_agents']))
    state[0] = np.random.normal(0, 0.5, config['n_agents']) # x
    state[1] = np.random.normal(0, 0.5, config['n_agents']) # p
    state[2] = np.random.rand(config['n_agents']) * 2 * np.pi # phi
    
    steps = 100
    dt = 0.01
    
    print("Running Python SwarmDynamics to generate spatial grid...")
    for i in range(steps):
        state = engine.step_rk4(state, dt)
            
    out_dir = Path("outputs/runs/expanded_emergence_2026-05-01/spatial_tda")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate an occupancy grid (resolution 50x50)
    res = 50
    grid = np.zeros((res, res))
    # Map agent positions [-5, 5] to [0, res-1]
    for x in state[0]:
        # Using a dummy 2D map: x vs p for visualization
        pass
    
    # Correct mapping for agent positions
    x = state[0]
    p = state[1]
    
    # Scale from approx [-3, 3] to [0, res-1]
    ix = ((x + 3) / 6 * (res - 1)).astype(int)
    iy = ((p + 3) / 6 * (res - 1)).astype(int)
    
    for i in range(config['n_agents']):
        if 0 <= ix[i] < res and 0 <= iy[i] < res:
            grid[iy[i], ix[i]] += 1.0
            
    # Normalize grid by max occupancy
    if grid.max() > 0:
        grid = grid / grid.max()
    
    grid_path = out_dir / "occupancy_grid.csv"
    np.savetxt(grid_path, grid, delimiter=",", fmt="%.4f")
    
    # Save metadata
    with open(out_dir / "meta.json", "w") as f:
        json.dump(config, f, indent=4)
        
    print(f"Spatial occupancy grid saved to {grid_path}")

if __name__ == "__main__":
    generate_spatial_grid()
