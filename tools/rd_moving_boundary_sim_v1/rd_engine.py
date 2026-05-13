import numpy as np

class RDEngine:
    def __init__(self, config):
        self.size = config['grid_size']
        self.dt = config['dt']
        
        # Numerical Conventions (AUDIT-004)
        self.boundary_mode = config.get('boundary_mode', 'periodic')
        self.dx = config.get('dx', 1.0)
        self.dy = config.get('dy', 1.0)
        
        # Coefficients
        self.D_diff = config['D_diff']
        self.S_diff = config['S_diff']
        self.beta = config['beta']
        self.theta_g = config['growth_thresh']
        self.gamma = config['domain_decay']
        self.alpha = config['signal_decay']
        
        # State
        self.D = np.zeros((self.size, self.size))
        self.S = np.zeros((self.size, self.size))
        
        # Initial small domain seed at source
        py, px = config['source_pos']
        r = config['source_radius']
        y, x = np.ogrid[:self.size, :self.size]
        mask = (x-px)**2 + (y-py)**2 <= r**2
        self.D[mask] = 1.0
        
        self.source_mask = mask
        self.source_strength = config['source_strength']

    def laplacian(self, field):
        """Standard 5-point stencil Laplacian."""
        up = np.roll(field, -1, axis=0)
        down = np.roll(field, 1, axis=0)
        left = np.roll(field, -1, axis=1)
        right = np.roll(field, 1, axis=1)
        return up + down + left + right - 4 * field

    def channeled_divergence(self, D, S):
        """Compute div(D * grad S)."""
        # Right flux: D_mid * (S_right - S_center)
        S_right = np.roll(S, -1, axis=1)
        D_right = np.roll(D, -1, axis=1)
        D_mid_x = 0.5 * (D + D_right)
        flux_x_right = D_mid_x * (S_right - S)
        
        # Left flux: D_mid * (S_center - S_left)
        S_left = np.roll(S, 1, axis=1)
        D_left = np.roll(D, 1, axis=1)
        D_mid_x_prev = 0.5 * (D + D_left)
        flux_x_left = D_mid_x_prev * (S - S_left)
        
        div_x = flux_x_right - flux_x_left
        
        # Down flux
        S_down = np.roll(S, -1, axis=0)
        D_down = np.roll(D, -1, axis=0)
        D_mid_y = 0.5 * (D + D_down)
        flux_y_down = D_mid_y * (S_down - S)
        
        # Up flux
        S_up = np.roll(S, 1, axis=0)
        D_up = np.roll(D, 1, axis=0)
        D_mid_y_prev = 0.5 * (D + D_up)
        flux_y_up = D_mid_y_prev * (S - S_up)
        
        div_y = flux_y_down - flux_y_up
        
        return div_x + div_y

    def step(self):
        # 1. Update Domain D
        # dD/dt = D_diff * lap(D) + beta * D(1-D)(S - theta) - gamma * D
        grad_term = self.beta * self.D * (1.0 - self.D) * (self.S - self.theta_g)
        dD = self.D_diff * self.laplacian(self.D) + grad_term - self.gamma * self.D
        
        # 2. Update Signal S
        # dS/dt = S_diff * div(D * grad S) + Source - alpha * S
        div_term = self.S_diff * self.channeled_divergence(self.D, self.S)
        dS = div_term - self.alpha * self.S
        dS[self.source_mask] += self.source_strength
        
        # Apply updates
        self.D += dD * self.dt
        self.S += dS * self.dt
        
        # Clipping
        self.D = np.clip(self.D, 0.0, 1.0)
        self.S = np.maximum(self.S, 0.0)

    def get_metrics(self):
        return {
            "active_area": np.sum(self.D),
            "total_signal": np.sum(self.S),
            "max_signal": np.max(self.S)
        }
