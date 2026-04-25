import numpy as np

class LBEngine:
    def __init__(self, config):
        self.nx = config['nx']
        self.ny = config['ny']
        self.tau = config['tau']
        self.u_inlet = config['u_inlet']
        self.threshold = config['erosion_threshold']
        
        # D2Q9 constants
        self.w = np.array([4/9, 1/9, 1/9, 1/9, 1/9, 1/36, 1/36, 1/36, 1/36])
        self.ex = np.array([0, 1, 0, -1, 0, 1, -1, -1, 1])
        self.ey = np.array([0, 0, 1, 0, -1, 1, 1, -1, -1])
        self.opp = np.array([0, 3, 4, 1, 2, 7, 8, 5, 6])
        
        # Distributions f[9, ny, nx]
        self.f = np.zeros((9, self.ny, self.nx))
        self.rho = np.ones((self.ny, self.nx))
        self.ux = np.zeros((self.ny, self.nx))
        self.uy = np.zeros((self.ny, self.nx))
        
        # Boundary mask: 1 is wall, 0 is fluid
        self.boundaries = np.zeros((self.ny, self.nx), dtype=bool)
        # Top and bottom walls
        self.boundaries[0, :] = True
        self.boundaries[-1, :] = True
        
        # Internal barrier (doorway)
        self.boundaries[:, self.nx // 2] = True
        # Create a small hole in the middle
        self.boundaries[self.ny // 2 - 2 : self.ny // 2 + 3, self.nx // 2] = False
        
        # Initialize f to equilibrium
        for i in range(9):
            self.f[i] = self.w[i] * self.rho

    def get_equilibrium(self, rho, ux, uy):
        feq = np.zeros((9, self.ny, self.nx))
        u2 = ux**2 + uy**2
        for i in range(9):
            eu = self.ex[i] * ux + self.ey[i] * uy
            feq[i] = self.w[i] * rho * (1 + 3*eu + 4.5*eu**2 - 1.5*u2)
        return feq

    def apply_boundaries(self, f_pre_streaming):
        # Standard Bounce-back
        for i in range(9):
            # For each boundary cell, set its f_i to the f_opposite from pre-streaming
            self.f[i, self.boundaries] = f_pre_streaming[self.opp[i], self.boundaries]

    def evolve(self):
        # Full iteration
        f_old = self.f.copy()
        
        # Collision
        self.rho = np.sum(self.f, axis=0)
        self.ux = np.sum(self.f * self.ex[:, None, None], axis=0) / self.rho
        self.uy = np.sum(self.f * self.ey[:, None, None], axis=0) / self.rho
        
        # Fix inlet
        self.ux[:, 0] = self.u_inlet
        self.uy[:, 0] = 0
        
        feq = self.get_equilibrium(self.rho, self.ux, self.uy)
        self.f += -(1.0 / self.tau) * (self.f - feq)
        
        # Save for bounce back
        f_post_collision = self.f.copy()
        
        # Streaming
        for i in range(9):
            self.f[i] = np.roll(np.roll(self.f[i], self.ex[i], axis=1), self.ey[i], axis=0)
            
        # Bounce back
        self.apply_boundaries(f_post_collision)
        
        # Erosion logic
        self.erode()

    def erode(self):
        # Momentum magnitude
        momentum = self.rho * np.sqrt(self.ux**2 + self.uy**2)
        
        # Potential erosion: check walls adjacent to fluid
        # We look for walls where at least one neighbor has high momentum
        # Simple: blur momentum and check at wall locations
        from scipy.ndimage import uniform_filter
        avg_momentum = uniform_filter(momentum, size=3)
        
        to_erode = self.boundaries & (avg_momentum > self.threshold)
        
        # Do not erode top and bottom boundaries (optional)
        to_erode[0, :] = False
        to_erode[-1, :] = False
        
        if np.any(to_erode):
            self.boundaries[to_erode] = False
            # Initialize eroded cells to average local fluid state
            # (already done by collision/streaming in next steps, but helps stability)
            pass

    def get_metrics(self):
        return {
            "fluid_volume": float(np.sum(~self.boundaries)),
            "mean_velocity": float(np.mean(np.sqrt(self.ux**2 + self.uy**2)[~self.boundaries]))
        }
