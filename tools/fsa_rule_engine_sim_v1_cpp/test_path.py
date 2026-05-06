import os
import platform
from pathlib import Path
import ctypes

def test():
    lib_name = "fsa_capi.dll"
    p = Path(__file__).parent / lib_name
    print(f"Checking path: {p}")
    print(f"Exists: {p.exists()}")
    print(f"Absolute: {p.resolve()}")
    
    if p.exists():
        try:
            lib = ctypes.CDLL(str(p.resolve()))
            print("Successfully loaded library")
        except Exception as e:
            print(f"Failed to load: {e}")

if __name__ == "__main__":
    test()
