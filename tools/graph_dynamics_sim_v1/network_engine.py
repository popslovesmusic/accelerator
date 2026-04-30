import numpy as np

class NetworkDynamics:
    def __init__(self, config):
        self.config = config
        self.n = config['n_nodes']
        self.K = config['K_phi']
        self.omega = np.random.normal(config['omega_mean'], config['omega_std'], size=(self.n,))
        
        # Adjacency Matrix A (Topological CSI)
        prob = config['initial_edge_prob']
        self.A = (np.random.rand(self.n, self.n) < prob).astype(float)
        np.fill_diagonal(self.A, 0)
        # Make symmetric for undirected graph
        self.A = np.maximum(self.A, self.A.T)
        
        # Thresholds
        self.theta_decouple = config['decouple_threshold']
        self.theta_recouple = config['recouple_threshold']
        self.P_recouple = config['recouple_prob']

    def get_derivatives(self, phi):
        """Standard Kuramoto phase update constrained by topology A."""
        dphi_mat = phi[np.newaxis, :] - phi[:, np.newaxis]
        coupling = np.sum(self.A * np.sin(dphi_mat), axis=1)
        dphi = self.omega + (self.K / self.n) * coupling
        return dphi

    def step_phi(self, phi, dt):
        """RK4 step for node phases."""
        k1 = self.get_derivatives(phi)
        k2 = self.get_derivatives(phi + 0.5 * dt * k1)
        k3 = self.get_derivatives(phi + 0.5 * dt * k2)
        k4 = self.get_derivatives(phi + dt * k3)
        
        new_phi = phi + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        return new_phi % (2 * np.pi)

    def rewire(self, phi):
        """Update topology based on phase alignment stress."""
        dphi_mat = phi[np.newaxis, :] - phi[:, np.newaxis]
        stress = np.abs(np.sin(dphi_mat))
        
        # 1. Decouple: Break edges where stress is high
        mask_decouple = (stress > self.theta_decouple) & (self.A > 0)
        self.A[mask_decouple] = 0
        
        # 2. Recouple: Add edges where stress is low
        mask_candidate = (stress < self.theta_recouple) & (self.A == 0)
        # Only add with probability P_recouple to avoid instant full connection
        mask_recouple = (np.random.rand(self.n, self.n) < self.P_recouple) & mask_candidate
        np.fill_diagonal(mask_recouple, False)
        self.A[mask_recouple] = 1
        
        # Keep symmetric
        self.A = np.maximum(self.A, self.A.T)

    def get_metrics(self, phi):
        # Topological metrics
        degrees = np.sum(self.A, axis=1)
        avg_degree = np.mean(degrees)
        edge_count = np.sum(self.A) // 2
        
        # Phase coherence (global order parameter)
        order_param = np.abs(np.mean(np.exp(1j * phi)))
        
        return {
            "avg_degree": avg_degree,
            "edge_count": int(edge_count),
            "order_parameter": order_param
        }
