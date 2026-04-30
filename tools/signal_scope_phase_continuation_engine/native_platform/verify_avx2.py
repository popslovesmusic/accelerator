import numpy as np
from tools.signal_scope_phase_continuation_engine.native_platform.phase_space import compute_phase_vector, phase_mismatch, HAS_AVX2

def verify_equivalence():
    print(f"HAS_AVX2: {HAS_AVX2}")
    if not HAS_AVX2:
        print("AVX2 not loaded, cannot verify equivalence.")
        return

    W = np.array([0.1, 0.2, 0.3])
    C = 0.4
    E = 0.5
    V = np.array([0.6, 0.7, 0.8])

    # Reference (forcing HAS_AVX2=False temporarily)
    import tools.signal_scope_phase_continuation_engine.native_platform.phase_space as ps
    ps.HAS_AVX2 = False
    phi_ref = ps.compute_phase_vector(W, C, E, V)
    mismatch_ref = ps.phase_mismatch(phi_ref, phi_ref * 0.9)

    # AVX2
    ps.HAS_AVX2 = True
    phi_avx = ps.compute_phase_vector(W, C, E, V)
    mismatch_avx = ps.phase_mismatch(phi_avx, phi_avx * 0.9)

    print(f"Phi Ref: {phi_ref}")
    print(f"Phi AVX: {phi_avx}")
    phi_delta = np.linalg.norm(phi_ref - phi_avx)
    print(f"Phi Delta: {phi_delta}")

    print(f"Mismatch Ref: {mismatch_ref}")
    print(f"Mismatch AVX: {mismatch_avx}")
    mismatch_delta = abs(mismatch_ref - mismatch_avx)
    print(f"Mismatch Delta: {mismatch_delta}")

    if phi_delta < 1e-6 and mismatch_delta < 1e-6:
        print("✅ Backend Equivalence Verified!")
    else:
        print("❌ Backend Equivalence FAILED!")

if __name__ == "__main__":
    verify_equivalence()
