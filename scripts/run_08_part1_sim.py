import os
import json
import numpy as np
from pathlib import Path
import sys

# Add tool paths
sys.path.append(str(Path("tools/kuramoto_sim_v1_cpp")))
from kuramoto_cpp_wrapper import KuramotoEngineCPP

def run_sim():
    run_id = "2026-05-23_run08_Relational_Asymmetry"
    out_dir = Path(f"results/{run_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "data").mkdir(exist_ok=True)

    n = 3
    kuramoto = KuramotoEngineCPP(n)
    kuramoto.omega[0] = 1.0
    kuramoto.omega[1] = 1.2
    kuramoto.omega[2] = 1.05

    steps = 1000
    phi_history = np.zeros((steps, n))
    
    print("Running 3-node asymmetry simulation...")
    for i in range(steps):
        kuramoto.run(dt=0.05, K=0.5, steps=1)
        phi_history[i] = kuramoto.phi.copy()

    np.save(out_dir / "data/phi_history.npy", phi_history)
    print("Simulation complete. Data saved.")

if __name__ == "__main__":
    run_sim()
