import ctypes
import os
import platform
from pathlib import Path

class CAEngineCPP:
    def __init__(self, width, height, lib_path=None):
        if lib_path is None:
            ext = ".dll" if platform.system() == "Windows" else ".so"
            lib_name = f"ca_capi{ext}"
            search_paths = [
                Path(__file__).parent / lib_name,
                Path(__file__).parent / "build" / lib_name,
            ]
            for p in search_paths:
                if p.exists():
                    lib_path = str(p)
                    break
        
        if not lib_path:
            raise FileNotFoundError("Could not find ca_capi shared library.")

        self.lib = ctypes.CDLL(lib_path)
        
        self.lib.create_ca_engine.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.create_ca_engine.restype = ctypes.c_void_p
        
        self.lib.destroy_ca_engine.argtypes = [ctypes.c_void_p]
        
        self.lib.set_ca_params.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_double]
        
        self.lib.initialize_ca.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_int, ctypes.c_double]
        
        self.lib.step_ca.argtypes = [ctypes.c_void_p]
        
        self.lib.get_ca_metrics.argtypes = [
            ctypes.c_void_p, 
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)
        ]

        self.obj = self.lib.create_ca_engine(width, height)

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj'):
            self.lib.destroy_ca_engine(self.obj)

    def set_params(self, D, delta_R, gamma_R):
        self.lib.set_ca_params(self.obj, D, delta_R, gamma_R)

    def initialize(self, source_strength, source_radius, initial_residue):
        self.lib.initialize_ca(self.obj, source_strength, source_radius, initial_residue)

    def step(self):
        self.lib.step_ca(self.obj)

    def get_metrics(self):
        active_frac, mean_e, mean_r = ctypes.c_double(), ctypes.c_double(), ctypes.c_double()
        self.lib.get_ca_metrics(self.obj, ctypes.byref(active_frac), ctypes.byref(mean_e), ctypes.byref(mean_r))
        return {
            "active_fraction": active_frac.value,
            "mean_mismatch": mean_e.value,
            "mean_residue": mean_r.value
        }
