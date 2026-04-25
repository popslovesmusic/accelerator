import numpy as np

class SwarmDynamics:
    def __init__(self, config):
        self.config = config
        self.n = config['n_agents']
        self.kappa = config['kappa']
        self.R_c = config['R_c']
        self.K_phi = config['K_phi']
        self.omega = np.random.normal(config['omega_mean'], config['omega_std'], self.n)
        self.mismatch_rate = config['mismatch_rate']
        self.residue_decay = config['residue_decay']
        
    def get_derivatives(self, state):
        """
        state is an array of [x, p, phi, residue, mismatch] for all agents.
        Shape: (5, n)
        """
        x = state[0]
        p = state[1]
        phi = state[2]
        res = state[3]
        mis = state[4]
        
        # 1. Kinematics
        dx = p
        dp = -self.kappa * x
        
        # 2. CSI Coupling Matrix
        # distance in phase space (x, p)
        dx_mat = x[:, np.newaxis] - x[np.newaxis, :]
        dp_mat = p[:, np.newaxis] - p[np.newaxis, :]
        dist_sq = dx_mat**2 + dp_mat**2
        C = (dist_sq < self.R_c**2).astype(float)
        
        # 3. Phase Dynamics (Kuramoto with CSI)
        dphi_mat = phi[np.newaxis, :] - phi[:, np.newaxis]
        phase_coupling = np.sum(C * np.sin(dphi_mat), axis=1)
        dphi = self.omega + (self.K_phi / self.n) * phase_coupling
        
        # 4. Mismatch & Residue
        # Mismatch grows, but is relaxed by local coherence
        # Local coherence: average cos of phase difference with neighbors
        neighbor_count = np.sum(C, axis=1)
        local_coherence = np.sum(C * np.cos(dphi_mat), axis=1) / np.maximum(neighbor_count, 1)
        
        dmis = self.mismatch_rate - 0.1 * local_coherence * mis
        dres = mis - self.residue_decay * res
        
        return np.array([dx, dp, dphi, dres, dmis])

    def step_rk4(self, state, dt):
        k1 = self.get_derivatives(state)
        k2 = self.get_derivatives(state + 0.5 * dt * k1)
        k3 = self.get_derivatives(state + 0.5 * dt * k2)
        k4 = self.get_derivatives(state + dt * k3)
        
        new_state = state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        
        # Normalize phase to [0, 2pi]
        new_state[2] = new_state[2] % (2 * np.pi)
        
        return new_state

    def compute_metrics(self, state):
        x = state[0]
        p = state[1]
        phi = state[2]
        
        # 1. Recalculate C and dphi_mat for metrics
        dx_mat = x[:, np.newaxis] - x[np.newaxis, :]
        dp_mat = p[:, np.newaxis] - p[np.newaxis, :]
        dist_sq = dx_mat**2 + dp_mat**2
        C = (dist_sq < self.R_c**2).astype(float)
        
        dphi_mat = phi[np.newaxis, :] - phi[:, np.newaxis]
        
        # 2. Compute Metrics
        order_param = np.abs(np.mean(np.exp(1j * phi)))
        
        neighbor_count = np.sum(C, axis=1)
        # Avoid division by zero
        local_coherence = np.sum(C * np.cos(dphi_mat), axis=1) / np.maximum(neighbor_count, 1)
        
        return {
            "x_mean": np.mean(x),
            "x_rms": np.std(x),
            "p_rms": np.std(p),
            "order_parameter": order_param,
            "local_coherence_mean": np.mean(local_coherence),
            "residue_mean": np.mean(state[3]),
            "mismatch_mean": np.mean(state[4])
        }
