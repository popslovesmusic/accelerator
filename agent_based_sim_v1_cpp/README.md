# AgentEngineAVX2 (High-Performance C++ Port)

This is a high-performance C++ implementation of the `agent_based_sim_v1` swarm dynamics simulation.

## Key Improvements
- **O(N) Spatial Hashing:** Replaces the O(N^2) neighbor search with an efficient grid-based lookup.
- **AVX2 & OpenMP:** Vectorized RK4 integration and multi-core parallelization.
- **Symplectic Treatment:** Focused on phase-space stability for swarm agents.
- **Python Integration:** C-API and `ctypes` wrapper for first-class Python support.

## Building
Use the provided `build_and_run.bat` (Windows/MSVC) or the following command for GCC:
```bash
g++ -O3 -mavx2 -fopenmp main.cpp AgentEngineAVX2.cpp -o agent_sim
```

## Performance
Designed to handle swarms of 10^4 to 10^5 agents with high-fidelity coupling rules.

## Future GPU Offloading (Intel UHD 770)
The SoA architecture and Spatial Hash are designed for migration to **oneAPI (SYCL)**. For very large swarms (>10^5), a SYCL-based tiled interaction kernel will provide substantial speedups.
