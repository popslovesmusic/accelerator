import ctypes
import numpy as np
import os

class MetricsEngineCPP:
    def __init__(self):
        # Add oneAPI bin directory to DLL search path on Windows
        if os.name == 'nt':
            oneapi_bin = r"C:\Program Files (x86)\Intel\oneAPI\compiler\latest\bin"
            if os.path.exists(oneapi_bin):
                os.add_dll_directory(oneapi_bin)
            oneapi_compiler_bin = r"C:\Program Files (x86)\Intel\oneAPI\compiler\latest\bin\compiler"
            if os.path.exists(oneapi_compiler_bin):
                os.add_dll_directory(oneapi_compiler_bin)

        dll_path = os.path.join(os.path.dirname(__file__), "metrics_engine.dll")
        if os.name == 'nt':
            self.lib = ctypes.CDLL(dll_path, winmode=0)
        else:
            self.lib = ctypes.CDLL(dll_path)
        
        self.lib.create_metrics_engine.restype = ctypes.c_void_p
        self.lib.destroy_metrics_engine.argtypes = [ctypes.c_void_p]
        
        self.lib.compute_entropy_sycl.argtypes = [
            ctypes.c_void_p, 
            ctypes.POINTER(ctypes.c_float), 
            ctypes.c_size_t, 
            ctypes.c_float, 
            ctypes.c_float, 
            ctypes.c_int
        ]
        self.lib.compute_entropy_sycl.restype = ctypes.c_float
        
        self.lib.compute_mutual_information_sycl.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_size_t,
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_int
        ]
        self.lib.compute_mutual_information_sycl.restype = ctypes.c_float
        
        self.engine = self.lib.create_metrics_engine()

    def __del__(self):
        if hasattr(self, 'engine') and self.engine:
            self.lib.destroy_metrics_engine(self.engine)

    def compute_entropy(self, data, bins=100, range=None):
        if range is None:
            min_val, max_val = float(np.min(data)), float(np.max(data))
        else:
            min_val, max_val = float(range[0]), float(range[1])
            
        data_float = data.astype(np.float32)
        n = data_float.size
        data_ptr = data_float.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        
        return self.lib.compute_entropy_sycl(self.engine, data_ptr, n, min_val, max_val, bins)

    def compute_mutual_information(self, x, y, bins=100, x_range=None, y_range=None):
        if x_range is None:
            x_min, x_max = float(np.min(x)), float(np.max(x))
        else:
            x_min, x_max = float(x_range[0]), float(x_range[1])
            
        if y_range is None:
            y_min, y_max = float(np.min(y)), float(np.max(y))
        else:
            y_min, y_max = float(y_range[0]), float(y_range[1])
            
        x_f = x.astype(np.float32)
        y_f = y.astype(np.float32)
        n = x_f.size
        
        x_ptr = x_f.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        y_ptr = y_f.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        
        return self.lib.compute_mutual_information_sycl(self.engine, x_ptr, y_ptr, n, x_min, x_max, y_min, y_max, bins)
