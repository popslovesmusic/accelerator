import ctypes
import os
import platform
from pathlib import Path

class AgentEngineCPP:
    def __init__(self, agent_count, lib_path=None):
        if lib_path is None:
            ext = ".dll" if platform.system() == "Windows" else ".so"
            lib_name = f"agent_capi{ext}"
            search_paths = [
                Path(__file__).parent / lib_name,
                Path(__file__).parent / "build" / lib_name,
            ]
            for p in search_paths:
                if p.exists():
                    lib_path = str(p)
                    break
        
        if not lib_path:
            raise FileNotFoundError("Could not find agent_capi shared library.")

        self.lib = ctypes.CDLL(lib_path)
        
        self.lib.create_agent_engine.argtypes = [ctypes.c_size_t]
        self.lib.create_agent_engine.restype = ctypes.c_void_p
        
        self.lib.destroy_agent_engine.argtypes = [ctypes.c_void_p]
        
        self.lib.set_swarm_params.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
        
        self.lib.initialize_swarm.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
        
        self.lib.step_swarm.argtypes = [ctypes.c_void_p, ctypes.c_double]
        
        self.lib.get_swarm_metrics.argtypes = [
            ctypes.c_void_p, 
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), 
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)
        ]

        self.obj = self.lib.create_agent_engine(agent_count)

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj'):
            self.lib.destroy_agent_engine(self.obj)

    def set_params(self, kappa, R_c, K_phi, mismatch_rate, residue_decay):
        self.lib.set_swarm_params(self.obj, kappa, R_c, K_phi, mismatch_rate, residue_decay)

    def initialize(self, seed, x_std, p_std, omega_mean, omega_std):
        self.lib.initialize_swarm(self.obj, seed, x_std, p_std, omega_mean, omega_std)

    def step(self, dt):
        self.lib.step_swarm(self.obj, dt)

    def get_metrics(self):
        x_mean, x_rms, order_param, res_mean = ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double()
        self.lib.get_swarm_metrics(self.obj, ctypes.byref(x_mean), ctypes.byref(x_rms), ctypes.byref(order_param), ctypes.byref(res_mean))
        return {
            "x_mean": x_mean.value,
            "x_rms": x_rms.value,
            "order_parameter": order_param.value,
            "residue_mean": res_mean.value
        }
