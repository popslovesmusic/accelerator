import ctypes
import os
import platform
from pathlib import Path

class FSAEngineCPP:
    def __init__(self, num_agents, n_states, forbidden, res_thresh, res_req, mismatch_rate=0.0, lib_path=None):
        if lib_path is None:
            ext = ".dll" if platform.system() == "Windows" else ".so"
            lib_name = f"fsa_capi{ext}"
            search_paths = [
                Path(__file__).parent / lib_name,
                Path(__file__).parent / "build" / lib_name,
            ]
            for p in search_paths:
                if p.exists():
                    lib_path = str(p)
                    break
        
        if not lib_path:
            raise FileNotFoundError("Could not find fsa_capi shared library.")

        self.lib = ctypes.CDLL(lib_path)
        
        self.lib.create_fsa_engine.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double]
        self.lib.create_fsa_engine.restype = ctypes.c_void_p
        
        self.lib.destroy_fsa_engine.argtypes = [ctypes.c_void_p]
        self.lib.initialize_fsa.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self.lib.step_fsa.argtypes = [ctypes.c_void_p]
        
        self.lib.get_fsa_metrics.argtypes = [
            ctypes.c_void_p, 
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_double)
        ]

        self.lib.get_active_history.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)
        ]

        self.obj = self.lib.create_fsa_engine(num_agents, n_states, forbidden, res_thresh, res_req, mismatch_rate)

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj'):
            self.lib.destroy_fsa_engine(self.obj)

    def initialize(self, start_node, seed):
        self.lib.initialize_fsa(self.obj, start_node, seed)

    def step(self):
        self.lib.step_fsa(self.obj)

    def get_metrics(self):
        active_count = ctypes.c_int()
        mean_res = ctypes.c_double()
        self.lib.get_fsa_metrics(self.obj, ctypes.byref(active_count), ctypes.byref(mean_res))
        return {
            "active_count": active_count.value,
            "mean_residue": mean_res.value
        }

    def get_active_history(self):
        size = ctypes.c_int()
        self.lib.get_active_history(self.obj, None, ctypes.byref(size))
        history = (ctypes.c_int * size.value)()
        self.lib.get_active_history(self.obj, history, ctypes.byref(size))
        return list(history)
