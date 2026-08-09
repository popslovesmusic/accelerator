import numpy as np
import json
import argparse
from pathlib import Path

class SATPHiggs1DReference:
    """
    Reference Implementation for SATP Higgs 1D (Coupled Wave Equations).
    Mechanism Class: reaction_diffusion
    Governing M-Laws: M8, M14
    """
    def __init__(self, n=128, dt=0.01, kappa=0.1, dx=1.0):
        self.n = n
        self.dt = dt
        self.kappa = kappa
        self.dx = dx
        
        # States: phi, h and their velocities
        self.phi = np.zeros(n)
        self.v_phi = np.zeros(n)
        self.h = np.ones(n) # Higgs field starts at VEV-ish
        self.v_h = np.zeros(n)
        
        # Potential parameters (M14 Closure Rule: phi and h must be consistent)
        self.lambda_h = 0.1
        self.g = 0.05
        self.vev = 1.0

    def get_accelerations(self, phi, h):
        """
        Wave equation with coupled potential.
        d2phi/dt2 = Laplacian(phi) - dV/dphi
        d2h/dt2 = Laplacian(h) - dV/dh
        """
        # Second derivative (Laplacian)
        d2phi_dx2 = (np.roll(phi, 1) - 2*phi + np.roll(phi, -1)) / (self.dx**2)
        d2h_dx2 = (np.roll(h, 1) - 2*h + np.roll(h, -1)) / (self.dx**2)
        
        # dV/dphi = g * phi * (h^2 - vev^2)
        dv_dphi = self.g * phi * (h**2 - self.vev**2)
        
        # dV/dh = lambda_h * h * (h^2 - vev^2) + 0.5 * g * phi^2 * h
        dv_dh = self.lambda_h * h * (h**2 - self.vev**2) + 0.5 * self.g * (phi**2) * h
        
        a_phi = d2phi_dx2 - dv_dphi
        a_h = d2h_dx2 - dv_dh
        
        return a_phi, a_h

    def update(self):
        """Velocity Verlet Integration."""
        # 1. Half step velocity
        a_phi, a_h = self.get_accelerations(self.phi, self.h)
        v_phi_half = self.v_phi + 0.5 * a_phi * self.dt
        v_h_half = self.v_h + 0.5 * a_h * self.dt
        
        # 2. Full step position
        self.phi += v_phi_half * self.dt
        self.h += v_h_half * self.dt
        
        # 3. New acceleration
        a_phi_new, a_h_new = self.get_accelerations(self.phi, self.h)
        
        # 4. Final half step velocity
        self.v_phi = v_phi_half + 0.5 * a_phi_new * self.dt
        self.v_h = v_h_half + 0.5 * a_h_new * self.dt
        
        return self.phi, self.h

def run_reference_sim(config, out_dir):
    n = config.get("n", 128)
    steps = config.get("steps", 100)
    dt = config.get("dt", 0.01)
    kappa = config.get("kappa", 0.1)
    
    sim = SATPHiggs1DReference(n=n, dt=dt, kappa=kappa)
    
    # Kick the field with some noise
    sim.phi += np.random.randn(n) * 0.1
    
    history = []
    for s in range(steps):
        phi, h = sim.update()
        
        if s % 10 == 0 or s == steps - 1:
            history.append({
                "step": s,
                "phi_rms": float(np.sqrt(np.mean(phi**2))),
                "h_rms": float(np.sqrt(np.mean(h**2)))
            })
            
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "reference_results.json", "w") as f:
        json.dump(history, f, indent=2)
    
    print(f"Reference Higgs 1D simulation complete. Results in {out_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    
    with open(args.config, "r") as f:
        config = json.load(f)
        
    run_reference_sim(config, args.out)
