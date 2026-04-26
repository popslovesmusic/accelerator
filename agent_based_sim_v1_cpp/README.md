# AgentEngineAVX2 (High-Performance C++ Port)

This is a high-performance C++ implementation of the `agent_based_sim_v1` swarm dynamics simulation.

## Key Improvements
- **O(N) Spatial Hashing:** Replaces the O(N^2) neighbor search with an efficient grid-based lookup.
- **AVX2 & OpenMP:** Vectorized RK4 integration and multi-core parallelization.
- **Symplectic Treatment:** Focused on phase-space stability for swarm agents.
- **Python Integration:** C-API and `ctypes` wrapper for first-class Python support.

## GPU Offloading (Intel UHD 770)
The engine includes `AgentEngineSYCL.hpp` which utilizes **oneAPI (SYCL)** to offload swarm interaction kernels directly to the GPU.
- **Optimization:** Kernels are adapted for **Single Precision (FP32)** to ensure compatibility with Intel UHD 770 hardware.
- **Performance:** Significant speedups for large swarms (>10^5 agents) via parallel force calculation.

## Building
### CPU (AVX2)
```bash
g++ -O3 -mavx2 -fopenmp main.cpp AgentEngineAVX2.cpp -o agent_sim
```

### GPU (SYCL)
```bash
icpx -fsycl -O3 AgentEngineSYCL.cpp -o agent_sim_gpu
```
