# LBFluidEngineSYCL (High-Performance C++ Port)

This is a high-performance C++ implementation of the `lb_fluid_sim_v1` Lattice Boltzmann fluid simulation.

## Key Improvements
- **D2Q9 Lattice Boltzmann:** Standard 9-velocity model for robust 2D fluid dynamics.
- **SYCL/GPU Acceleration:** Full offloading of the collision and streaming kernels to the Intel UHD 770.
- **Pull-Streaming Architecture:** Optimized for GPU memory patterns to avoid race conditions and maximize throughput.
- **Single-Precision Optimization:** Kernels use FP32 for compatibility with integrated Intel GPUs.
- **Erosion Support:** Compatible with dynamic boundary updates for corridor/pocket research.
- **Python Integration:** C-API and `ctypes` wrapper for interactive fluid research.

## GPU Offloading (Intel UHD 770)
The engine includes `LBFluidEngineSYCL.hpp` which utilizes **oneAPI (SYCL)** to offload the LBM steps directly to the GPU.
- **Performance:** Significant throughput gains (>30 million cell updates/sec).

## Building
### CPU/GPU (SYCL)
Use the provided `build_and_run.bat` (Windows/oneAPI) or:
```bash
icpx -fsycl -O3 -shared lb_capi.cpp -o lb_engine.dll
```

## Usage
### Python
```python
from lb_cpp_wrapper import LBEngineCPP
engine = LBEngineCPP(nx=256, ny=128)
engine.initialize_equilibrium(rho_init=1.0)
engine.run(tau=0.6, u_inlet=0.1, steps=100)
# Velocity fields are available as engine.ux, engine.uy (numpy views)
```
