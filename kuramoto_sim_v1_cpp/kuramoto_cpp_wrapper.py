import ctypes
import numpy as np
import os

class KuramotoEngineCPP:
    def __init__(self, n):
        self.n = n
        if os.name == 'nt':
            # Add oneAPI bin directory to DLL search path
            oneapi_bin = r"C:\Program Files (x86)\Intel\oneAPI\compiler\latest\bin"
            if os.path.exists(oneapi_bin):
                os.add_dll_directory(oneapi_bin)
            oneapi_compiler_bin = r"C:\Program Files (x86)\Intel\oneAPI\compiler\latest\bin\compiler"
            if os.path.exists(oneapi_compiler_bin):
                os.add_dll_directory(oneapi_compiler_bin)

        dll_path = os.path.join(os.path.dirname(__file__), "kuramoto_engine.dll")
        if os.name == 'nt':
            self.lib = ctypes.CDLL(dll_path, winmode=0)
        else:
            self.lib = ctypes.CDLL(dll_path)
            
        self.lib.create_kuramoto_engine.argtypes = [ctypes.c_size_t]
        self.lib.create_kuramoto_engine.restype = ctypes.c_void_p
        
        self.lib.destroy_kuramoto_engine.argtypes = [ctypes.c_void_p]
        
        self.lib.get_phi_ptr.argtypes = [ctypes.c_void_p]
        self.lib.get_phi_ptr.restype = ctypes.POINTER(ctypes.c_float)
        
        self.lib.get_omega_ptr.argtypes = [ctypes.c_void_p]
        self.lib.get_omega_ptr.restype = ctypes.POINTER(ctypes.c_float)
        
        self.lib.run_steps.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float, ctypes.c_int]
        
        self.lib.get_order_parameter.argtypes = [ctypes.c_void_p]
        self.lib.get_order_parameter.restype = ctypes.c_float
        
        self.obj = self.lib.create_kuramoto_engine(n)
        
        # Expose buffers as numpy arrays
        phi_ptr = self.lib.get_phi_ptr(self.obj)
        self.phi = np.ctypeslib.as_array(phi_ptr, shape=(n,))
        
        omega_ptr = self.lib.get_omega_ptr(self.obj)
        self.omega = np.ctypeslib.as_array(omega_ptr, shape=(n,))

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj') and self.obj:
            self.lib.destroy_kuramoto_engine(self.obj)

    def run(self, dt, K, steps):
        self.lib.run_steps(self.obj, dt, K, steps)

    def get_order_parameter(self):
        return self.lib.get_order_parameter(self.obj)
