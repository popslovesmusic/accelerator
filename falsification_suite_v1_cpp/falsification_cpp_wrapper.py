import ctypes
import os
import platform
import json
from pathlib import Path

class FalsificationEngineCPP:
    def __init__(self, num_threads=0, lib_path=None):
        if lib_path is None:
            ext = ".dll" if platform.system() == "Windows" else ".so"
            lib_name = f"falsification_capi{ext}"
            search_paths = [
                Path(__file__).parent / lib_name,
                Path(__file__).parent / "build" / lib_name,
            ]
            for p in search_paths:
                if p.exists():
                    lib_path = str(p)
                    break
        
        if not lib_path:
            raise FileNotFoundError("Could not find falsification_capi shared library.")

        self.lib = ctypes.CDLL(lib_path)
        
        self.lib.create_falsification_runner.argtypes = [ctypes.c_int]
        self.lib.create_falsification_runner.restype = ctypes.c_void_p
        
        self.lib.destroy_falsification_runner.argtypes = [ctypes.c_void_p]
        
        self.lib.run_falsification_suite.argtypes = [
            ctypes.c_void_p, 
            ctypes.c_char_p, 
            ctypes.c_char_p, 
            ctypes.c_int
        ]

        self.obj = self.lib.create_falsification_runner(num_threads)

    def __del__(self):
        if hasattr(self, 'lib') and hasattr(self, 'obj'):
            self.lib.destroy_falsification_runner(self.obj)

    def run_suite(self, suite_json):
        if not isinstance(suite_json, str):
            suite_json = json.dumps(suite_json)
        
        # Max report size 1MB for now
        max_len = 1024 * 1024
        report_buffer = ctypes.create_string_buffer(max_len)
        
        self.lib.run_falsification_suite(
            self.obj, 
            suite_json.encode('utf-8'), 
            report_buffer, 
            max_len
        )
        
        return json.loads(report_buffer.value.decode('utf-8'))
