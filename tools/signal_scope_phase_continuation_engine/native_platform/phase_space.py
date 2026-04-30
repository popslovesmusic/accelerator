import numpy as np
import os
import ctypes

# Load AVX2 Backend if available
DLL_PATH = os.path.join(os.path.dirname(__file__), "phase_core_avx2.dll")
HAS_AVX2 = False
if os.path.exists(DLL_PATH):
    try:
        _lib = ctypes.CDLL(DLL_PATH)
        _lib.compute_phase_vector_avx2.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.c_float, ctypes.c_float,
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)
        ]
        _lib.phase_mismatch_avx2.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)
        ]
        _lib.phase_mismatch_avx2.restype = ctypes.c_float
        HAS_AVX2 = True
    except Exception as e:
        print(f"Warning: Failed to load AVX2 backend: {e}")

def normalize(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v

def compute_phase_vector(W, C, E, V):
    if HAS_AVX2:
        W_arr = np.ascontiguousarray(W, dtype=np.float32)
        V_arr = np.ascontiguousarray(V, dtype=np.float32)
        out = np.zeros(8, dtype=np.float32)
        _lib.compute_phase_vector_avx2(
            W_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            float(C), float(E),
            V_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        )
        return out
    
    # Reference Implementation (Double Precision)
    W = np.asarray(W, dtype=float)
    V = np.asarray(V, dtype=float)
    phase = np.array([
        2.0 * W[0], 2.0 * W[1], 2.0 * W[2],
        1.5 * C, 1.5 * E,
        2.0 * V[0], 2.0 * V[1], 2.0 * V[2]
    ], dtype=float)
    return normalize(phase)

def phase_mismatch(phi1, phi2):
    if HAS_AVX2:
        phi1_arr = np.ascontiguousarray(phi1, dtype=np.float32)
        phi2_arr = np.ascontiguousarray(phi2, dtype=np.float32)
        return float(_lib.phase_mismatch_avx2(
            phi1_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            phi2_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        ))

    # Reference Implementation
    dot = float(np.dot(phi1, phi2))
    dot = max(-1.0, min(1.0, dot))
    return 1.0 - dot
