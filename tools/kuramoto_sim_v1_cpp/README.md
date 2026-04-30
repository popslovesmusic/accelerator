# KuramotoEngineSYCL (High-Performance C++ Port)

This is a high-performance C++ implementation of the `kuramoto_sim_v1` oscillators simulation.

## Key Improvements
- **RK4 Integration:** High-precision integration for phase dynamics.
- **1D Ring Coupling:** Vectorized neighbor interaction kernel.
- **SYCL/GPU Acceleration:** Full offloading of the integration and coupling kernels to the Intel UHD 770.
- **Single-Precision Optimization:** Optimized for integrated GPUs (FP32).
- **Python Integration:** C-API and `ctypes` wrapper for interactive research.

## GPU Offloading (Intel UHD 770)
The engine includes `KuramotoEngineSYCL.hpp` which utilizes **oneAPI (SYCL)** to offload the RK4 steps directly to the GPU.
- **Performance:** Significant throughput gains for large oscillator counts (>10^5).

## Building
### CPU/GPU (SYCL)
Use the provided `build_and_run.bat` (Windows/oneAPI) or:
```bash
icpx -fsycl -O3 -shared kuramoto_capi.cpp -o kuramoto_engine.dll
```

## Usage
### Python
```python
from kuramoto_cpp_wrapper import KuramotoEngineCPP
engine = KuramotoEngineCPP(n=100000)
engine.omega[:] = np.random.normal(0, 0.1, 100000)
engine.run(dt=0.1, K=0.5, steps=100)
print(f"Order Parameter: {engine.get_order_parameter()}")
```
