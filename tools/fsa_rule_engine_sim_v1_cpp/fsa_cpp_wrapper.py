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
            raise FileNotFoundError(f"Could not find {lib_name} shared library in {[str(p) for p in search_paths]}")

        # On Windows, we might need to add the library directory and its dependencies to the DLL search path
        if platform.system() == "Windows":
            lib_dir = str(Path(lib_path).parent.resolve())
            try:
                os.add_dll_directory(lib_dir)
            except Exception as e:
                print(f"Warning: Could not add {lib_dir} to DLL directory: {e}")

            # Also add oneAPI/SYCL directories from PATH
            path_env = os.environ.get("PATH", "")
            added_count = 0
            for directory in path_env.split(";"):
                if not directory or not os.path.isdir(directory):
                    continue
                
                dir_lower = directory.lower()
                # Check for oneAPI or Intel related directories that might contain SYCL DLLs
                if "oneapi" in dir_lower or "intel" in dir_lower or "sycl" in dir_lower:
                    try:
                        # Be a bit more specific: check if directory contains any .dll files
                        # (optional, but helps avoid adding empty or irrelevant folders)
                        has_dlls = any(f.endswith(".dll") for f in os.listdir(directory))
                        if has_dlls:
                            os.add_dll_directory(os.path.abspath(directory))
                            added_count += 1
                    except Exception:
                        pass
            
            if added_count > 0:
                print(f"Added {added_count} oneAPI/Intel/SYCL directories from PATH to DLL search path.")

        print(f"Loading library from: {lib_path}")
        try:
            # winmode=0 can also be used on Python 3.8+ to use the default search order (including PATH)
            # but os.add_dll_directory is the preferred modern way.
            self.lib = ctypes.CDLL(lib_path)
        except Exception as e:
            print(f"\nFATAL ERROR: Could not load {lib_path}")
            print(f"Error detail: {e}")
            print(f"System PATH: {os.environ.get('PATH')}")
            if platform.system() == "Windows":
                print("Checking for common oneAPI dependencies in PATH...")
                missing = []
                for dep in ["sycl7.dll", "pi_win_proxy_loader.dll", "libmmd.dll"]:
                    found = False
                    for directory in path_env.split(";"):
                        if os.path.exists(os.path.join(directory, dep)):
                            found = True
                            print(f"  [FOUND] {dep} in {directory}")
                            break
                    if not found:
                        missing.append(dep)
                if missing:
                    print(f"  [MISSING] {missing}")
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
        history = (ctypes.c_int * size.value)()
        self.lib.get_active_history(self.obj, history, ctypes.byref(size))
        return list(history)
