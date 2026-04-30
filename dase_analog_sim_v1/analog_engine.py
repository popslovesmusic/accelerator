import numpy as np

class AnalogEngine:
    def __init__(self, n_nodes):
        self.n_nodes = n_nodes
        self.current_output = np.zeros(n_nodes)
        self.integrator_state = np.zeros(n_nodes)
        self.feedback_gain = np.zeros(n_nodes)
        
    def step(self, input_val, control_val, bias_val, dt, iterations):
        for _ in range(iterations):
            # Simple analog-integrator model: dV/dt = gain * (in - V)
            # This matches the core loop in the SYCL port
            error = input_val - self.current_output
            self.integrator_state += (self.feedback_gain * error + control_val + bias_val) * dt
            
            # Simple clamping for stability
            self.integrator_state = np.clip(self.integrator_state, -10.0, 10.0)
            self.current_output = self.integrator_state
            
    def get_metrics(self):
        return {
            "mean_output": float(np.mean(self.current_output)),
            "max_output": float(np.max(self.current_output)),
            "mean_integrator": float(np.mean(self.integrator_state))
        }
