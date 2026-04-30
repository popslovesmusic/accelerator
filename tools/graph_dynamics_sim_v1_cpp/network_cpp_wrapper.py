import ctypes
import os
import platform
from pathlib import Path

class NetworkEngineCPP:
    def __init__(self, n_nodes, lib_path=None):
        if lib_path is None:
            ext = ".dll" if platform.system() == "Windows" else ".so"
            lib_name = f"network_capi{ext}"
            search_paths = [
                Path(__file__).parent / lib_name,
                Path(__file__).parent / "build" / lib_name,
            ]
            for p in search_paths:
                if p.exists():
                    lib_path = str(p)
                    break
        
        if not lib_path:
            raise FileNotFoundError("Could not find network_capi shared library.")

        self.lib = ctypes.CDLL(lib_path)
        
        self.lib.create_network_engine.argtypes = [ctypes.c_int]
        self.lib.create_network_engine.restype = ctypes.c_void_p
        
        self.lib.destroy_network_engine.argtypes = [ctypes.c_void_p]
        
        self.lib.set_network_params.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
        
        self.lib.initialize_network.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_double]
        
        self.lib.step_network.argtypes = [ctypes.c_void_p, ctypes.c_double]
        self.lib.rewire_network.argtypes = [ctypes.c_void_p]
        
        self.lib.get_network_metrics.argtypes = [
            ctypes.c_void_p, 
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_double)
        ]

        self.obj = self.lib.create_network_engine(n_nodes)

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj'):
            self.lib.destroy_network_engine(self.obj)

    def set_params(self, K, theta_de, theta_re, P_re):
        self.lib.set_network_params(self.obj, K, theta_de, theta_re, P_re)

    def initialize(self, seed, omega_mean, omega_std):
        self.lib.initialize_network(self.obj, seed, omega_mean, omega_std)

    def step(self, dt):
        self.lib.step_network(self.obj, dt)

    def rewire(self):
        self.lib.rewire_network(self.obj)

    def get_metrics(self):
        avg_deg, edge_count, order_param = ctypes.c_double(), ctypes.c_int(), ctypes.c_double()
        self.lib.get_network_metrics(self.obj, ctypes.byref(avg_deg), ctypes.byref(edge_count), ctypes.byref(order_param))
        return {
            "avg_degree": avg_deg.value,
            "edge_count": edge_count.value,
            "order_parameter": order_param.value
        }
