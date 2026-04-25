import numpy as np

class KuramotoEngine:
    def __init__(self, config):
        self.config = config
        self.n = config['n_oscillators']
        self.K = config['K']
        
        if config['omega_dist'] == 'gaussian':
            self.omega = np.random.normal(config['omega_mean'], config['omega_std'], size=self.n)
        else:
            self.omega = np.random.uniform(config['omega_mean'] - config['omega_std'], 
                                           config['omega_mean'] + config['omega_std'], size=self.n)
            
    def get_derivatives(self, phi):
        """1D Ring coupling: dphi = omega + K * (sin(phi_next - phi) + sin(phi_prev - phi))"""
        phi_next = np.roll(phi, -1)
        phi_prev = np.roll(phi, 1)
        
        coupling = np.sin(phi_next - phi) + np.sin(phi_prev - phi)
        dphi = self.omega + self.K * coupling
        return dphi

    def step_rk4(self, phi, dt):
        k1 = self.get_derivatives(phi)
        k2 = self.get_derivatives(phi + 0.5 * dt * k1)
        k3 = self.get_derivatives(phi + 0.5 * dt * k2)
        k4 = self.get_derivatives(phi + dt * k3)
        
        new_phi = phi + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        return new_phi % (2 * np.pi)

    def compute_metrics(self, phi):
        # Global Order Parameter R
        # R * exp(i*psi) = 1/N * sum(exp(i*phi))
        z = np.mean(np.exp(1j * phi))
        order_parameter = np.abs(z)
        
        # Local Coherence (average over 5-neighbor window)
        # Using complex mean for local synchronization measure
        exp_phi = np.exp(1j * phi)
        local_z = (np.roll(exp_phi, 2) + np.roll(exp_phi, 1) + exp_phi + 
                   np.roll(exp_phi, -1) + np.roll(exp_phi, -2)) / 5.0
        local_coherence = np.mean(np.abs(local_z))
        
        return {
            "order_parameter": float(order_parameter),
            "local_coherence_mean": float(local_coherence)
        }
