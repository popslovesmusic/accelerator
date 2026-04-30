import ctypes
import numpy as np
import os

class LBEngineCPP:
    def __init__(self, nx, ny):
        self.nx = nx
        self.ny = ny
        if os.name == 'nt':
            # Add oneAPI bin directory to DLL search path
            oneapi_bin = r"C:\Program Files (x86)\Intel\oneAPI\compiler\latest\bin"
            if os.path.exists(oneapi_bin):
                os.add_dll_directory(oneapi_bin)

        dll_path = os.path.join(os.path.dirname(__file__), "lb_engine.dll")
        if os.name == 'nt':
            self.lib = ctypes.CDLL(dll_path, winmode=0)
        else:
            self.lib = ctypes.CDLL(dll_path)
            
        self.lib.create_lb_engine.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.create_lb_engine.restype = ctypes.c_void_p
        
        self.lib.destroy_lb_engine.argtypes = [ctypes.c_void_p]
        
        self.lib.initialize_lb_equilibrium.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_float]
        self.lib.set_lb_mask.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int, ctypes.c_int]
        self.lib.run_lb_steps.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float, ctypes.c_int]
        
        self.lib.get_lb_ux_ptr.argtypes = [ctypes.c_void_p]
        self.lib.get_lb_ux_ptr.restype = ctypes.POINTER(ctypes.c_float)
        
        self.lib.get_lb_uy_ptr.argtypes = [ctypes.c_void_p]
        self.lib.get_lb_uy_ptr.restype = ctypes.POINTER(ctypes.c_float)
        
        self.lib.get_lb_rho_ptr.argtypes = [ctypes.c_void_p]
        self.lib.get_lb_rho_ptr.restype = ctypes.POINTER(ctypes.c_float)
        
        self.obj = self.lib.create_lb_engine(nx, ny)
        
        # Expose buffers
        ux_ptr = self.lib.get_lb_ux_ptr(self.obj)
        self.ux = np.ctypeslib.as_array(ux_ptr, shape=(ny, nx))
        
        uy_ptr = self.lib.get_lb_uy_ptr(self.obj)
        self.uy = np.ctypeslib.as_array(uy_ptr, shape=(ny, nx))
        
        rho_ptr = self.lib.get_lb_rho_ptr(self.obj)
        self.rho = np.ctypeslib.as_array(rho_ptr, shape=(ny, nx))

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj') and self.obj:
            self.lib.destroy_lb_engine(self.obj)

    def initialize_equilibrium(self, rho_init=1.0):
        self.lib.initialize_lb_equilibrium(self.obj, self.nx, self.ny, rho_init)

    def set_mask(self, mask):
        mask_uint8 = mask.astype(np.uint8)
        self.lib.set_lb_mask(self.obj, mask_uint8.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)), self.nx, self.ny)

    def run(self, tau, u_inlet, steps):
        self.lib.run_lb_steps(self.obj, tau, u_inlet, steps)
