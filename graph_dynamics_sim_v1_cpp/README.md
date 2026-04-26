# NetworkDynamicsAVX2 (High-Performance C++ Port)

This is a high-performance C++ implementation of the `graph_dynamics_sim_v1` dynamic network simulation.

## Key Improvements
- **Vectorized Interaction Kernel:** Uses AVX2 to compute Kuramoto couplings across node pairs simultaneously.
- **SIMD Rewiring:** Fast evaluation of topological stress using vectorized math.
- **OpenMP Parallelization:** Multi-threaded integration of the phase equations and adjacency matrix updates.
- **Python Integration:** C-API and `ctypes` wrapper for first-class Python support.

## GPU Offloading (Intel UHD 770)
The engine includes `NetworkEngineSYCL.hpp` which utilizes **oneAPI (SYCL)** to offload coupling and rewiring kernels to the GPU.
- **Optimization:** Kernels are adapted for **Single Precision (FP32)** for Intel UHD 770 compatibility.
- **Performance:** Real-time simulation of multi-thousand node networks with zero CPU contention.

## Building
### CPU (AVX2)
```bash
g++ -O3 -mavx2 -fopenmp main.cpp NetworkEngineAVX2.cpp -o network_sim
```

### GPU (SYCL)
```bash
icpx -fsycl -O3 NetworkEngineSYCL.cpp -o network_gpu
```
