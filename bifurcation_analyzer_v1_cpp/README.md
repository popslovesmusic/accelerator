# BifurcationAnalyzerAVX2 (High-Performance C++ Port)

This is a high-performance C++ implementation of the `bifurcation_analyzer_v1`.

## Key Improvements
- **Exponential Speedup:** Native C++ execution of parameter sweeps.
- **Lyapunov Stability:** Automatic calculation of maximal Lyapunov exponents to detect chaos.
- **RK4/Map Support:** Designed to wrap both discrete maps and continuous ODEs.
- **Python Integration:** C-API and `ctypes` wrapper for real-time regime mapping.

## Building
Use the provided `build_and_run.bat` (Windows/MSVC) or the following command for GCC:
```bash
g++ -O3 -mavx2 -fopenmp main.cpp BifurcationEngine.cpp -o bifurcation_sim
```

## Future GPU Offloading (Intel UHD 770)
For massive parameter scans (e.g., 2D parameter planes), a **oneAPI (SYCL)** kernel can evaluate thousands of stability points in parallel, providing immediate "phase diagrams" of the system.
