import numpy as np
import json
import argparse
import os
from pathlib import Path

class PhaseLagPilotSim:
    """
    Exploratory Simulator for LFCR_004: Phase-Lagged Relational Closure.
    Implements a modified Sakaguchi-Kuramoto model with residue memory.
    """
    def __init__(self, n_nodes=2, seed=42):
        self.n = n_nodes
        self.seed = seed
        np.random.seed(seed)
        
        # Primitives
        self.phi = np.random.uniform(0, 2*np.pi, n_nodes)
        self.omega = np.random.normal(1.0, 0.1, n_nodes)
        self.residue = np.zeros((n_nodes, n_nodes))
        
    def step(self, dt, K, alpha, decay_r):
        n = self.n
        dphi = np.zeros(n)
        
        # Current Relation State (Admissibility Check)
        # We calculate the phase difference including the lag (alpha)
        # alpha acts as the Delta_phi_R in the formal expression
        for i in range(n):
            coupling = 0.0
            for j in range(n):
                if i == j: continue
                
                # Relation: D(j|i) -> phi_j - phi_i
                # Phase-lagged recurrence: (phi_j - phi_i) - alpha
                diff = (self.phi[j] - self.phi[i]) - alpha
                
                # Update Residue (Memory of the relation)
                # In this pilot, residue tracks the persistence of the phase coherence
                self.residue[i, j] = (self.residue[i, j] * (1 - decay_r) + 
                                     np.cos(diff) * decay_r)
                
                # Update phase based on coupling and residue
                # The residue 'conditions' the strength of the return
                coupling += K * np.sin(diff) * (1.0 + self.residue[i, j])
                
            dphi[i] = self.omega[i] + coupling / n
            
        self.phi += dt * dphi
        self.phi = np.mod(self.phi, 2*np.pi)
        
    def get_observables(self):
        # Closure Strength: order parameter R = |1/N sum(exp(i*phi))|
        order_p = np.abs(np.mean(np.exp(1j * self.phi)))
        
        # Phase Lag Coherence: how stable is the delta_phi relative to alpha?
        # For N=2, we just look at the stability of the difference
        if self.n == 2:
            diff = np.mod(self.phi[1] - self.phi[0], 2*np.pi)
            return {
                "S_closure": float(order_p),
                "phi_diff_mean": float(diff),
                "R_residue": float(np.mean(self.residue))
            }
        return {
            "S_closure": float(order_p),
            "R_residue": float(np.mean(self.residue))
        }

def main():
    parser = argparse.ArgumentParser(description="LFCR_004 Phase-Lag Pilot Simulator")
    parser.add_argument("--config", required=True, help="Path to config JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()
    
    with open(args.config, 'r') as f:
        config = json.load(f)
        
    os.makedirs(args.out, exist_ok=True)
    
    # Extract params
    n_nodes = config.get("n_nodes", 2)
    steps = config.get("steps", 1000)
    dt = config.get("dt", 0.05)
    K = config.get("K", 1.0)
    alpha = config.get("alpha", 0.0) # Delta_phi_R
    decay_r = config.get("decay_r", 0.05)
    seed = config.get("seed", 42)
    
    sim = PhaseLagPilotSim(n_nodes=n_nodes, seed=seed)
    
    history = []
    for i in range(steps):
        sim.step(dt, K, alpha, decay_r)
        if i % 100 == 0:
            history.append(sim.get_observables())
            
    final_metrics = sim.get_observables()
    
    with open(Path(args.out) / "summary.json", "w") as f:
        json.dump({
            "config": config,
            "final_metrics": final_metrics,
            "history": history
        }, f, indent=2)

if __name__ == "__main__":
    main()
