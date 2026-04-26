# CAAdmissibilityAVX2 (High-Performance C++ Port)

This is a high-performance C++ implementation of the `ca_admissibility_sim_v1` 2D Cellular Automata.

## Key Improvements
- **AVX2 Stencils:** Vectorized 5-point Laplacian and 4-neighbor gradient calculations.
- **Gated Diffusion:** SIMD-masked updates where local gradient exceeds residue.
- **OpenMP Scaling:** Multi-core parallelization for large grid processing.
- **Python Integration:** C-API and `ctypes` wrapper for interactive research.

## Building
Use the provided `build_and_run.bat` (Windows/MSVC) or the following command for GCC:
```bash
g++ -O3 -mavx2 -fopenmp main.cpp CAEngineAVX2.cpp -o ca_sim
```

## Performance
Optimized for massive 2D grids (e.g., 2048x2048 and beyond).

## Future GPU Offloading (Intel UHD 770)
The local stencil nature of this simulation is ideal for **oneAPI (SYCL)**. Moving the transition rules to the GPU will allow real-time simulation of multi-million cell grids with zero CPU overhead.
