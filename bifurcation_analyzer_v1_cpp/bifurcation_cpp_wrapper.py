import ctypes
import os
import platform
import numpy as np
from pathlib import Path

class BifurcationEngineCPP:
    def __init__(self, lib_path=None):
        if lib_path is None:
            ext = ".dll" if platform.system() == "Windows" else ".so"
            lib_name = f"bifurcation_capi{ext}"
            search_paths = [
                Path(__file__).parent / lib_name,
                Path(__file__).parent / "build" / lib_name,
            ]
            for p in search_paths:
                if p.exists():
                    lib_path = str(p)
                    break
        
        if not lib_path:
            raise FileNotFoundError("Could not find bifurcation_capi shared library.")

        self.lib = ctypes.CDLL(lib_path)
        
        self.lib.create_bifurcation_engine.restype = ctypes.c_void_p
        self.lib.destroy_bifurcation_engine.argtypes = [ctypes.c_void_p]
        
        self.lib.run_bifurcation_sweep.argtypes = [
            ctypes.c_void_p,
            ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)
        ]

        self.obj = self.lib.create_bifurcation_engine()

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj'):
            self.lib.destroy_bifurcation_engine(self.obj)

    def run_sweep(self, start, end, steps, plateau_len):
        params = np.zeros(steps, dtype=np.float64)
        means = np.zeros(steps, dtype=np.float64)
        lyaps = np.zeros(steps, dtype=np.float64)
        
        self.lib.run_bifurcation_sweep(
            self.obj, start, end, steps, plateau_len,
            params.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            means.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            lyaps.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        )
        
        return {
            "parameters": params,
            "means": means,
            "lyapunov": lyaps
        }
