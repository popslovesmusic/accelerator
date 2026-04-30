# CircularEngineAVX2 (High-Performance C++ Port)

This is a high-performance C++ implementation of the `circular_accelerator_sim_v1` ring dynamics simulation.

## Key Improvements
- **Symplectic Integrity:** 4th-order Yoshida Integrator for precise multi-turn tracking.
- **AVX2 & OpenMP:** Vectorized particle dynamics and multi-core parallelization.
- **Turn-by-Turn Optimization:** Optimized longitudinal wrapping and phase-space mapping.
- **Python Integration:** C-API and `ctypes` wrapper for first-class Python support.

## GPU Offloading (Intel UHD 770)
The engine includes `CircularEngineSYCL.hpp` which utilizes **oneAPI (SYCL)** to offload particle tracking to the GPU.
- **Optimization:** Kernels use **Single Precision (FP32)** for Intel UHD 770.
- **Performance:** Real-time tracking of multi-million particles with high numerical stability.

## Building
### CPU (AVX2)
```bash
g++ -O3 -mavx2 -fopenmp main.cpp CircularEngineAVX2.cpp -o ring_sim
```

### GPU (SYCL)
```bash
icpx -fsycl -O3 CircularEngineSYCL.cpp -o ring_gpu
```
