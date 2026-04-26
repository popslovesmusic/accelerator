# CircularEngineAVX2 (High-Performance C++ Port)

This is a high-performance C++ implementation of the `circular_accelerator_sim_v1` ring dynamics simulation.

## Key Improvements
- **Symplectic Integrity:** 4th-order Yoshida Integrator for precise multi-turn tracking.
- **AVX2 & OpenMP:** Vectorized particle dynamics and multi-core parallelization.
- **Turn-by-Turn Optimization:** Optimized longitudinal wrapping and phase-space mapping.
- **Python Integration:** C-API and `ctypes` wrapper for first-class Python support.

## Building
Use the provided `build_and_run.bat` (Windows/MSVC) or the following command for GCC:
```bash
g++ -O3 -mavx2 -fopenmp main.cpp CircularEngineAVX2.cpp -o ring_sim
```

## Performance
Designed to track 10^6 particles for 10^4+ turns with high numerical stability.

## Future GPU Offloading (Intel UHD 770)
The turn-by-turn nature of this simulation is ideal for **oneAPI (SYCL)**. Offloading the lattice traversal to the GPU will allow real-time visualization of beam stability and multi-million turn studies.
