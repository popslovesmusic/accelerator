import numpy as np
import json
import argparse
from pathlib import Path
from scipy.fft import fftn, ifftn

class IGSOAGWReference:
    """
    Reference Implementation for IGSOA GW Core (3D Symmetry Field).
    Mechanism Class: reaction_diffusion
    Governing M-Laws: M1, M8, M9, M12
    """
    def __init__(self, nx=32, ny=32, nz=32, alpha=1.5, kappa=0.1, lambda_r=0.01):
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.alpha = alpha  # Fractional order
        self.kappa = kappa  # Inscription/coupling rate
        self.lambda_r = lambda_r  # Decay rate
        
        self.phi = np.zeros((nx, ny, nz), dtype=np.float64)
        self.residue = np.zeros((nx, ny, nz), dtype=np.float64)
        
        # Precompute fractional Laplacian kernel in Fourier space
        kx = np.fft.fftfreq(nx).reshape(-1, 1, 1)
        ky = np.fft.fftfreq(ny).reshape(1, -1, 1)
        kz = np.fft.fftfreq(nz).reshape(1, 1, -1)
        k2 = kx**2 + ky**2 + kz**2
        self.frac_lap_kernel = -(k2**(alpha / 2.0))
        
    def fractional_laplacian(self, field):
        """M8: Deviation Propagation via transport frame."""
        f_field = fftn(field)
        return np.real(ifftn(f_field * self.frac_lap_kernel))

    def update(self, sources=None):
        """
        Core update rule: 
        phi' = phi + Pi_A( kappa * Delta^alpha phi + sources ) - lambda * phi
        """
        # 1. Compute propagation (RHS of MLaw core)
        propagation = self.fractional_laplacian(self.phi)
        
        # 2. Add sources
        raw_increment = self.kappa * propagation
        if sources is not None:
            raw_increment += sources
            
        # 3. M4/M7: Admissibility Projection (Simplified for reference)
        # In this reference, we use a simple threshold-based projection
        admissible_increment = np.where(np.abs(raw_increment) < 1.0, raw_increment, 0.0)
        
        # 4. M6: Residue Inscription
        self.residue += self.kappa * admissible_increment - self.lambda_r * self.residue
        
        # 5. State update
        self.phi += admissible_increment - self.lambda_r * self.phi
        
        return self.phi

def run_reference_sim(config, out_dir):
    nx = config.get("nx", 32)
    ny = config.get("ny", 32)
    nz = config.get("nz", 32)
    steps = config.get("steps", 100)
    alpha = config.get("alpha", 1.5)
    kappa = config.get("kappa", 0.1)
    
    sim = IGSOAGWReference(nx=nx, ny=ny, nz=nz, alpha=alpha, kappa=kappa)
    
    history = []
    for s in range(steps):
        # Dummy binary merger source (two Gaussian blobs moving)
        sources = np.zeros((nx, ny, nz))
        t = s / steps
        p1 = np.array([nx/2 + 5*np.cos(2*np.pi*t), ny/2 + 5*np.sin(2*np.pi*t), nz/2])
        p2 = np.array([nx/2 - 5*np.cos(2*np.pi*t), ny/2 - 5*np.sin(2*np.pi*t), nz/2])
        
        for p in [p1, p2]:
            x, y, z = np.indices((nx, ny, nz))
            dist2 = (x - p[0])**2 + (y - p[1])**2 + (z - p[2])**2
            sources += np.exp(-dist2 / 2.0)
            
        phi = sim.update(sources=sources)
        
        if s % 10 == 0 or s == steps - 1:
            history.append({
                "step": s,
                "phi_rms": float(np.sqrt(np.mean(phi**2))),
                "energy_density": float(np.sum(phi**2)),
                "echo_intensity": float(np.max(np.abs(phi)))
            })
            
    # Save results
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "reference_results.json", "w") as f:
        json.dump(history, f, indent=2)
    
    print(f"Reference simulation complete. Results in {out_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    
    with open(args.config, "r") as f:
        config = json.load(f)
        
    run_reference_sim(config, args.out)
