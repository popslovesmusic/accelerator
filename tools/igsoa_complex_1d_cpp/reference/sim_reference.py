import numpy as np
import json
import argparse
from pathlib import Path

class IGSOAComplex1DReference:
    """
    Reference Implementation for IGSOA Complex 1D Lattice.
    Mechanism Class: cellular_automata
    Governing M-Laws: M2, M3, M4, M6
    """
    def __init__(self, num_nodes=100, r_c=5, kappa=0.1, lambda_r=0.01):
        self.num_nodes = num_nodes
        self.r_c = r_c
        self.kappa = kappa
        self.lambda_r = lambda_r
        
        # State: complex phi (represented as complex128)
        self.phi = np.zeros(num_nodes, dtype=np.complex128)
        self.residue = np.zeros(num_nodes, dtype=np.float64)
        
        # Initialize with small noise
        self.phi = (np.random.randn(num_nodes) + 1j*np.random.randn(num_nodes)) * 0.01

    def update(self):
        """
        Non-local coupling update:
        phi_i' = phi_i + kappa * sum_{j in range} (phi_j - phi_i)
        """
        new_phi = np.copy(self.phi)
        
        for i in range(self.num_nodes):
            # 1. M3: Collect distinguishable mismatch (complex difference)
            mismatch_sum = 0j
            count = 0
            for j in range(i - self.r_c, i + self.r_c + 1):
                idx = j % self.num_nodes # Periodic boundaries
                mismatch_sum += (self.phi[idx] - self.phi[i])
                count += 1
            
            # 2. M4: Selection/Projection
            raw_increment = (self.kappa / count) * mismatch_sum
            
            # 3. Update state
            new_phi[i] += raw_increment - self.lambda_r * self.phi[i]
            
            # 4. M6: Inscribe residue (energy density of the update)
            self.residue[i] += self.kappa * (np.abs(raw_increment)**2) - self.lambda_r * self.residue[i]
            
        self.phi = new_phi
        return self.phi

def run_reference_sim(config, out_dir):
    num_nodes = config.get("num_nodes", 100)
    steps = config.get("steps", 100)
    r_c = config.get("R_c", 5)
    kappa = config.get("kappa", 0.1)
    
    sim = IGSOAComplex1DReference(num_nodes=num_nodes, r_c=r_c, kappa=kappa)
    
    history = []
    for s in range(steps):
        phi = sim.update()
        
        if s % 10 == 0 or s == steps - 1:
            history.append({
                "step": s,
                "mean_phi": float(np.mean(np.abs(phi))),
                "psi_squared_mean": float(np.mean(np.abs(phi)**2)),
                "entropy_rate": float(np.std(np.angle(phi))) # Proxy for entropy
            })
            
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "reference_results.json", "w") as f:
        json.dump(history, f, indent=2)
    
    print(f"Reference 1D simulation complete. Results in {out_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    
    with open(args.config, "r") as f:
        config = json.load(f)
        
    run_reference_sim(config, args.out)
