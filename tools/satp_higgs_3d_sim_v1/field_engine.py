import numpy as np

class SATPHiggsEngine3D:
    def __init__(self, nx, ny, nz):
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.phi = np.zeros((nz, ny, nx))
        self.phi_prev = np.zeros((nz, ny, nx))
        self.h = np.zeros((nz, ny, nx))
        self.h_prev = np.zeros((nz, ny, nx))
        
    def initialize_vacuum(self, h_vev):
        self.h[:] = h_vev
        self.h_prev[:] = h_vev
        
    def step(self, dt, dx, h_vev, lambda_h, g):
        def laplacian(arr):
            lap = -6.0 * arr.copy()
            lap += np.roll(arr, 1, axis=0)
            lap += np.roll(arr, -1, axis=0)
            lap += np.roll(arr, 1, axis=1)
            lap += np.roll(arr, -1, axis=1)
            lap += np.roll(arr, 1, axis=2)
            lap += np.roll(arr, -1, axis=2)
            return lap / (dx * dx)

        m2 = -lambda_h * (h_vev ** 2)
        
        force_phi = laplacian(self.phi) - (g * (self.h**2) * self.phi)
        force_h   = laplacian(self.h) - (m2 * self.h + lambda_h * (self.h**3) + g * self.h * (self.phi**2))
        
        new_phi = 2.0 * self.phi - self.phi_prev + force_phi * (dt * dt)
        new_h   = 2.0 * self.h - self.h_prev + force_h * (dt * dt)
        
        self.phi_prev[:] = self.phi
        self.phi[:] = new_phi
        self.h_prev[:] = self.h
        self.h[:] = new_h
        
    def get_metrics(self, h_vev):
        phi_rms = np.sqrt(np.mean(self.phi ** 2))
        h_dev = self.h - h_vev
        h_rms = np.sqrt(np.mean(h_dev ** 2))
        return {
            "phi_rms": float(phi_rms),
            "higgs_rms": float(h_rms)
        }
