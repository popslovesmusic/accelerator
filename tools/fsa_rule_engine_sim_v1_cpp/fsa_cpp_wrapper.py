import ctypes
import os
import platform
from pathlib import Path

class FSAEngineCPP:
    def __init__(self, num_agents, n_states, forbidden, res_thresh, res_req, mismatch_rate=0.0, lib_path=None):
        if lib_path is None:
            ext = ".dll" if platform.system() == "Windows" else ".so"
            lib_name = f"fsa_capi{ext}"
            script_dir = Path(__file__).parent.resolve()
            search_paths = [
                script_dir / lib_name,
                script_dir / "build" / lib_name,
            ]
            for p in search_paths:
                if p.exists():
                    lib_path = str(p.resolve())
                    break
        
        if not lib_path:
            raise FileNotFoundError(f"Could not find shared library in {[str(p) for p in search_paths]}")

        # On Windows, we need to add the library directory and its dependencies to the DLL search path
        if platform.system() == "Windows":
            lib_dir = os.path.dirname(os.path.abspath(lib_path))
            try:
                os.add_dll_directory(lib_dir)
            except Exception as e:
                print(f"Warning: Could not add {lib_dir} to DLL directory: {e}")

            # Also add oneAPI/SYCL directories from PATH and common locations
            path_env = os.environ.get("PATH", "")
            potential_dirs = set()
            for directory in path_env.split(";"):
                if not directory or not os.path.isdir(directory):
                    continue
                dir_lower = directory.lower()
                if "oneapi" in dir_lower or "intel" in dir_lower or "sycl" in dir_lower:
                    potential_dirs.add(os.path.abspath(directory))

            # Common oneAPI/Intel locations if not in PATH
            common_locations = [
                r"C:\Program Files (x86)\Intel\oneAPI\compiler\latest\bin",
                r"C:\Program Files (x86)\Intel\oneAPI\compiler\latest\windows\bin",
                r"C:\Program Files\Intel\oneAPI\compiler\latest\bin",
                r"C:\Program Files\Intel\oneAPI\compiler\latest\windows\bin"
            ]
            for loc in common_locations:
                if os.path.isdir(loc):
                    potential_dirs.add(os.path.abspath(loc))

            for directory in potential_dirs:
                try:
                    # Check if directory contains any .dll files to avoid cluttering search path
                    if any(f.endswith(".dll") for f in os.listdir(directory)):
                        os.add_dll_directory(directory)
                except Exception:
                    pass

        print(f"Loading FSA CAPI library from: {lib_path}")
        try:
            self.lib = ctypes.CDLL(lib_path)
        except Exception as e:
            if platform.system() == "Windows":
                try:
                    # Fallback to LOAD_WITH_ALTERED_SEARCH_PATH
                    self.lib = ctypes.CDLL(lib_path, winmode=8)
                except Exception as e2:
                    print(f"FATAL: Failed to load DLL. Error: {e}, Fallback error: {e2}")
                    raise
            else:
                raise

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
        if size.value <= 0:
            return []
        history = (ctypes.c_int * size.value)()
        self.lib.get_active_history(self.obj, history, ctypes.byref(size))
        return list(history)
