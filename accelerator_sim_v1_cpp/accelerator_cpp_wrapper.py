import ctypes
import os
import platform
import json
from pathlib import Path

class AcceleratorEngineCPP:
    def __init__(self, particle_count, lib_path=None):
        if lib_path is None:
            # Default search paths
            ext = ".dll" if platform.system() == "Windows" else ".so"
            lib_name = f"accelerator_capi{ext}"
            search_paths = [
                Path(__file__).parent / lib_name,
                Path(__file__).parent / "build" / lib_name,
                Path(__file__).parent / "release" / lib_name,
            ]
            for p in search_paths:
                if p.exists():
                    lib_path = str(p)
                    break
        
        if not lib_path:
            raise FileNotFoundError("Could not find accelerator_capi shared library. Please build the C++ project.")

        self.lib = ctypes.CDLL(lib_path)
        
        # Define argtypes and restypes
        self.lib.create_engine.argtypes = [ctypes.c_size_t]
        self.lib.create_engine.restype = ctypes.c_void_p
        
        self.lib.destroy_engine.argtypes = [ctypes.c_void_p]
        
        self.lib.add_drift.argtypes = [ctypes.c_void_p, ctypes.c_double]
        self.lib.add_quadrupole.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double]
        self.lib.add_rf_cavity.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_double]
        self.lib.add_space_charge_2d.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double]
        
        self.lib.initialize_normal.argtypes = [
            ctypes.c_void_p, 
            ctypes.c_double, ctypes.c_double, 
            ctypes.c_double, ctypes.c_double, 
            ctypes.c_double, ctypes.c_double, 
            ctypes.c_int
        ]
        
        self.lib.run_simulation.argtypes = [ctypes.c_void_p, ctypes.c_int]
        
        self.lib.get_metrics.argtypes = [
            ctypes.c_void_p, 
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)
        ]

        self.obj = self.lib.create_engine(particle_count)

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj'):
            self.lib.destroy_engine(self.obj)

    def add_lattice_from_json(self, lattice_json):
        if isinstance(lattice_json, str):
            lattice_json = json.loads(lattice_json)
        
        for el in lattice_json:
            etype = el["type"]
            if etype == "drift":
                self.lib.add_drift(self.obj, float(el["length"]))
            elif etype == "quadrupole":
                self.lib.add_quadrupole(self.obj, float(el["k1"]), float(el["length"]))
            elif etype == "rf_cavity":
                self.lib.add_rf_cavity(self.obj, float(el["voltage"]), float(el["phase"]), float(el["harmonic"]))
            elif etype == "space_charge_2d":
                self.lib.add_space_charge_2d(self.obj, int(el["nx"]), int(el["ny"]), float(el["width"]), float(el["height"]))

    def initialize_normal(self, x_rms, px_rms, y_rms, py_rms, z_rms, delta_rms, seed):
        self.lib.initialize_normal(self.obj, x_rms, px_rms, y_rms, py_rms, z_rms, delta_rms, seed)

    def run(self, steps):
        self.lib.run_simulation(self.obj, steps)

    def get_metrics(self):
        x_mean = ctypes.c_double()
        x_rms = ctypes.c_double()
        survival = ctypes.c_double()
        self.lib.get_metrics(self.obj, ctypes.byref(x_mean), ctypes.byref(x_rms), ctypes.byref(survival))
        return {
            "x_mean": x_mean.value,
            "x_rms": x_rms.value,
            "survival": survival.value
        }
