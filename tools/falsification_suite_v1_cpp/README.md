# FalsificationSuiteAVX2 (High-Performance C++ Port)

This is a high-performance C++ implementation of the `falsification_suite_v1` unit test and validation harness.

## Key Improvements
- **Asynchronous Parallel Dispatch:** Executes multiple simulations concurrently using a thread pool.
- **Direct C-API Integration:** Designed to invoke native engine DLLs with zero process overhead.
- **Robust Logic:** Robust assertion evaluator for complex multi-metric validation.
- **Python Integration:** C-API and `ctypes` wrapper for first-class Python support.

## Building
Use the provided `build_and_run.bat` (Windows/MSVC) or the following command for GCC:
```bash
g++ -O3 -mavx2 -fopenmp main.cpp FalsificationRunner.cpp -o falsification_sim
```

## Performance
Capable of processing thousands of validation scenarios per second.

## Future GPU Offloading (Intel UHD 770)
For statistical falsification (e.g., Running 1000 seeds of a single configuration), a **oneAPI (SYCL)** kernel can execute the entire batch on the GPU, providing instant statistical confidence reports.
