import numpy as np
import json
import argparse
from pathlib import Path

class IGSOAComplex2DReference:
    """
    Reference Implementation for IGSOA Complex 2D Lattice.
    Mechanism Class: cellular_automata
    Governing M-Laws: M2, M3, M4, M6
    """
    def __init__(self, nx=32, ny=32, r_c=3, kappa=0.1, lambda_r=0.01):
        self.nx = nx
        self.ny = ny
        self.r_c = r_c
        self.kappa = kappa
        self.lambda_r = lambda_r
        
        # State: complex phi
        self.phi = (np.random.randn(nx, ny) + 1j*np.random.randn(nx, ny)) * 0.01
        self.residue = np.zeros((nx, ny), dtype=np.float64)

    def update(self):
        new_phi = np.copy(self.phi)
        
        for i in range(self.nx):
            for j in range(self.ny):
                # Collector (simplified)
                mismatch_sum = 0j
                count = 0
                for di in range(-self.r_c, self.r_c + 1):
                    for dj in range(-self.r_c, self.r_c + 1):
                        if di**2 + dj**2 <= self.r_c**2:
                            idx_i = (i + di) % self.nx
                            idx_j = (j + dj) % self.ny
                            mismatch_sum += (self.phi[idx_i, idx_j] - self.phi[i, j])
                            count += 1
                
                raw_increment = (self.kappa / count) * mismatch_sum
                new_phi[i, j] += raw_increment - self.lambda_r * self.phi[i, j]
                self.residue[i, j] += self.kappa * (np.abs(raw_increment)**2) - self.lambda_r * self.residue[i, j]
        
        self.phi = new_phi
        return self.phi

def run_reference_sim(config, out_dir):
    nx = config.get("nx", 32)
    ny = config.get("ny", 32)
    steps = config.get("steps", 100)
    r_c = config.get("R_c", 3)
    kappa = config.get("kappa", 0.1)
    
    sim = IGSOAComplex2DReference(nx=nx, ny=ny, r_c=r_c, kappa=kappa)
    
    history = []
    for s in range(steps):
        phi = sim.update()
        if s % 10 == 0 or s == steps - 1:
            history.append({
                "step": s,
                "mean_phi": float(np.mean(np.abs(phi))),
                "psi_squared_mean": float(np.mean(np.abs(phi)**2))
            })
            
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "reference_results.json", "w") as f:
        json.dump(history, f, indent=2)
    print(f"Reference 2D simulation complete. Results in {out_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with open(args.config, "r") as f:
        config = json.load(f)
    run_reference_sim(config, args.out)
