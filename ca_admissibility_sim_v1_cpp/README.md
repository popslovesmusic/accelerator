# CAAdmissibilityAVX2 (High-Performance C++ Port)

This is a high-performance C++ implementation of the `ca_admissibility_sim_v1` 2D Cellular Automata.

## Key Improvements
- **AVX2 Stencils:** Vectorized 5-point Laplacian and 4-neighbor gradient calculations.
- **Gated Diffusion:** SIMD-masked updates where local gradient exceeds residue.
- **OpenMP Scaling:** Multi-core parallelization for large grid processing.
- **Python Integration:** C-API and `ctypes` wrapper for interactive research.

## GPU Offloading (Intel UHD 770)
The engine includes `CAEngineSYCL.hpp` which utilizes **oneAPI (SYCL)** to offload transition rules to the GPU.
- **Optimization:** Kernels use **Single Precision (FP32)** for Intel UHD 770 compatibility.
- **Performance:** Real-time simulation of multi-million cell grids with zero CPU overhead.

## Building
### CPU (AVX2)
```bash
g++ -O3 -mavx2 -fopenmp main.cpp CAEngineAVX2.cpp -o ca_sim
```

### GPU (SYCL)
```bash
icpx -fsycl -O3 CAEngineSYCL.cpp -o ca_sim_gpu
```
