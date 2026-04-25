import numpy as np

class StochasticEngine:
    def __init__(self, config):
        self.config = config
        self.n = config['n_particles']
        self.kappa = config['kappa']
        self.sigma = config['sigma']
        self.x_thresh = config['x_thresh']
        self.dt = config['dt']
        
        # State: x position for all particles
        self.x = np.full(self.n, config['initial_x'])
        
        # Tracking: first passage times (onset times)
        self.onset_times = np.full(self.n, -1.0)
        self.has_crossed = np.zeros(self.n, dtype=bool)

    def step(self, current_time):
        """Euler-Maruyama step: dx = -k*x*dt + sigma*dW"""
        # Deterministic force (Gradient of quadratic potential U = 0.5 * k * x^2)
        force = -self.kappa * self.x
        
        # Stochastic force
        noise = self.sigma * np.random.normal(0, np.sqrt(self.dt), size=self.n)
        
        # Update
        self.x += force * self.dt + noise
        
        # Threshold detection
        crossing = (self.x >= self.x_thresh) & (~self.has_crossed)
        if np.any(crossing):
            self.onset_times[crossing] = current_time
            self.has_crossed[crossing] = True
            
        return self.has_crossed

    def get_metrics(self):
        return {
            "mean_x": np.mean(self.x),
            "std_x": np.std(self.x),
            "crossing_fraction": np.mean(self.has_crossed),
            "onset_count": int(np.sum(self.has_crossed))
        }
