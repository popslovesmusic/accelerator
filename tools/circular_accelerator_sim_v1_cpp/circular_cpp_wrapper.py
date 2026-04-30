import ctypes
import os
import platform
from pathlib import Path

class CircularEngineCPP:
    def __init__(self, particle_count, circumference, momentum_compaction, lib_path=None):
        if lib_path is None:
            ext = ".dll" if platform.system() == "Windows" else ".so"
            lib_name = f"circular_capi{ext}"
            search_paths = [
                Path(__file__).parent / lib_name,
                Path(__file__).parent / "build" / lib_name,
            ]
            for p in search_paths:
                if p.exists():
                    lib_path = str(p)
                    break
        
        if not lib_path:
            raise FileNotFoundError("Could not find circular_capi shared library.")

        self.lib = ctypes.CDLL(lib_path)
        
        self.lib.create_circular_engine.argtypes = [ctypes.c_size_t, ctypes.c_double, ctypes.c_double]
        self.lib.create_circular_engine.restype = ctypes.c_void_p
        
        self.lib.destroy_circular_engine.argtypes = [ctypes.c_void_p]
        
        self.lib.add_ring_drift.argtypes = [ctypes.c_void_p, ctypes.c_double]
        self.lib.add_ring_quadrupole.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double]
        self.lib.add_ring_rf_cavity.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
        self.lib.add_ring_aperture.argtypes = [ctypes.c_void_p, ctypes.c_double]
        
        self.lib.initialize_ring.argtypes = [
            ctypes.c_void_p, ctypes.c_int,
            ctypes.c_double, ctypes.c_double,
            ctypes.c_double, ctypes.c_double,
            ctypes.c_double, ctypes.c_double
        ]
        
        self.lib.run_ring.argtypes = [ctypes.c_void_p, ctypes.c_int]
        
        self.lib.get_ring_metrics.argtypes = [
            ctypes.c_void_p, ctypes.c_int,
            ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double)
        ]

        self.obj = self.lib.create_circular_engine(particle_count, circumference, momentum_compaction)

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj'):
            self.lib.destroy_circular_engine(self.obj)

    def add_drift(self, length):
        self.lib.add_ring_drift(self.obj, length)

    def add_quadrupole(self, k1, length):
        self.lib.add_ring_quadrupole(self.obj, k1, length)

    def add_rf_cavity(self, voltage, phase, harmonic, circumference):
        self.lib.add_ring_rf_cavity(self.obj, voltage, phase, harmonic, circumference)

    def add_aperture(self, radius):
        self.lib.add_ring_aperture(self.obj, radius)

    def initialize(self, seed, x_sigma, px_sigma, y_sigma, py_sigma, z_sigma, delta_sigma):
        self.lib.initialize_ring(self.obj, seed, x_sigma, px_sigma, y_sigma, py_sigma, z_sigma, delta_sigma)

    def run(self, turns):
        self.lib.run_ring(self.obj, turns)

    def get_metrics(self, turn):
        alive = ctypes.c_size_t()
        xr, yr, zr, dr = ctypes.c_double(), ctypes.c_double(), ctypes.c_double(), ctypes.c_double()
        self.lib.get_ring_metrics(self.obj, turn, ctypes.byref(alive), ctypes.byref(xr), ctypes.byref(yr), ctypes.byref(zr), ctypes.byref(dr))
        return {
            "turn": turn,
            "alive_count": alive.value,
            "x_rms": xr.value,
            "y_rms": yr.value,
            "z_rms": zr.value,
            "delta_rms": dr.value
        }
