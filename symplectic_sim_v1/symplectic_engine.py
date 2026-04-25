import numpy as np

class HamiltonianEngine:
    def __init__(self, config):
        self.n = config['n_particles']
        self.m = config['mass']
        self.kappa = config['kappa']
        self.dt = config['dt']
        
        # Initial State: q, p
        self.q = np.random.normal(0, config['initial_q_spread'], size=self.n)
        self.p = np.random.normal(0, config['initial_p_spread'], size=self.n)

    def grad_V(self, q):
        """Gradient of potential V = -kappa * cos(q) -> dV/dq = kappa * sin(q)"""
        return self.kappa * np.sin(q)

    def compute_hamiltonian(self, q, p):
        """H = T + V = p^2 / 2m - kappa * cos(q)"""
        T = p**2 / (2 * self.m)
        V = -self.kappa * np.cos(q)
        return T + V

    def step_leapfrog(self):
        """2nd order symplectic integrator (Position Verlet variant)."""
        dt = self.dt
        
        # 1. p half-step
        p_half = self.p - 0.5 * dt * self.grad_V(self.q)
        
        # 2. q full-step
        self.q = self.q + dt * (p_half / self.m)
        
        # 3. p full-step
        self.p = p_half - 0.5 * dt * self.grad_V(self.q)
        
        # Wrap q to [-pi, pi] for pendulum periodicity
        self.q = (self.q + np.pi) % (2 * np.pi) - np.pi

    def get_metrics(self):
        H = self.compute_hamiltonian(self.q, self.p)
        return {
            "mean_H": float(np.mean(H)),
            "std_H": float(np.std(H)),
            "mean_q": float(np.mean(self.q)),
            "mean_p": float(np.mean(self.p)),
            "q_rms": float(np.std(self.q)),
            "p_rms": float(np.std(self.p))
        }
