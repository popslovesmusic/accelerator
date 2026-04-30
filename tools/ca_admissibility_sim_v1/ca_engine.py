import numpy as np

class AdmissibilityCA:
    def __init__(self, config):
        self.size = config['grid_size']
        self.D = config['diffusion_rate']
        self.delta_R = config['residue_growth']
        self.gamma_R = config['residue_decay']
        self.seed = int(config.get("seed", 42))
        self.rng = np.random.default_rng(self.seed)

        self.epsilon_noise_std = float(config.get("epsilon_noise_std", 0.0))
        self.residue_noise_std = float(config.get("residue_noise_std", 0.0))
        
        # State: Mismatch (epsilon) and Residue (R)
        self.epsilon = np.zeros((self.size, self.size))
        self.R = np.full((self.size, self.size), config['initial_residue'])

        if self.epsilon_noise_std > 0.0:
            self.epsilon = self.epsilon + self.rng.normal(scale=self.epsilon_noise_std, size=self.epsilon.shape)

        if self.residue_noise_std > 0.0:
            self.R = self.R + self.rng.normal(scale=self.residue_noise_std, size=self.R.shape)
            self.R = np.maximum(self.R, 0.0)
        
        # Optional: Initialize a central source
        center = self.size // 2
        r = config.get('source_radius', 5)
        y, x = np.ogrid[-center:self.size-center, -center:self.size-center]
        mask = x*x + y*y <= r*r
        self.epsilon[mask] = config['source_strength']

    def get_gradient(self):
        """Compute the sum of absolute differences with 4-neighbors."""
        grad = np.zeros_like(self.epsilon)
        # Shifted versions for 4-neighbors
        up = np.roll(self.epsilon, -1, axis=0)
        down = np.roll(self.epsilon, 1, axis=0)
        left = np.roll(self.epsilon, -1, axis=1)
        right = np.roll(self.epsilon, 1, axis=1)
        
        grad = (np.abs(self.epsilon - up) + 
                np.abs(self.epsilon - down) + 
                np.abs(self.epsilon - left) + 
                np.abs(self.epsilon - right))
        return grad

    def get_laplacian(self):
        """Discrete Laplacian using 5-point stencil."""
        up = np.roll(self.epsilon, -1, axis=0)
        down = np.roll(self.epsilon, 1, axis=0)
        left = np.roll(self.epsilon, -1, axis=1)
        right = np.roll(self.epsilon, 1, axis=1)
        return up + down + left + right - 4 * self.epsilon

    def step(self):
        # 1. Calculate driving gradient
        delta = self.get_gradient()
        
        # 2. Admissibility Mask
        admissible = delta > self.R
        
        # 3. Update Epsilon (only where admissible)
        laplacian = self.get_laplacian()
        self.epsilon[admissible] += self.D * laplacian[admissible]
        
        # 4. Update Residue
        # R grows where active, decays everywhere
        self.R = self.R * (1 - self.gamma_R) + self.delta_R * admissible.astype(float)
        
        return admissible

    def get_metrics(self, admissible_mask):
        return {
            "active_fraction": np.mean(admissible_mask),
            "mean_mismatch": np.mean(self.epsilon),
            "max_mismatch": np.max(self.epsilon),
            "mean_residue": np.mean(self.R)
        }
