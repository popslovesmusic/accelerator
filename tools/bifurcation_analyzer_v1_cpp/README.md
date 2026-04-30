# BifurcationAnalyzerAVX2 (High-Performance C++ Port)

This is a high-performance C++ implementation of the `bifurcation_analyzer_v1`.

## Key Improvements
- **Exponential Speedup:** Native C++ execution of parameter sweeps.
- **Lyapunov Stability:** Automatic calculation of maximal Lyapunov exponents to detect chaos.
- **RK4/Map Support:** Designed to wrap both discrete maps and continuous ODEs.
- **Python Integration:** C-API and `ctypes` wrapper for real-time regime mapping.

## GPU Offloading (Intel UHD 770)
The engine includes `BifurcationEngineSYCL.hpp` which utilizes **oneAPI (SYCL)** to evaluate stability points in parallel.
- **Optimization:** Kernels use **Single Precision (FP32)** for Intel UHD 770.
- **Performance:** Instant generation of "phase diagrams" by mapping thousands of parameters simultaneously.

## Building
### CPU (AVX2)
```bash
g++ -O3 -mavx2 -fopenmp main.cpp BifurcationEngine.cpp -o bifurcation_sim
```

### GPU (SYCL)
```bash
icpx -fsycl -O3 BifurcationEngineSYCL.cpp -o bifurcation_gpu
```
