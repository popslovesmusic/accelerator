# AcceleratorEngineAVX2 (High-Performance C++ Port)

This is a high-performance, vectorized 6D accelerator simulation engine. It is a direct C++ port of the `accelerator_sim_v1` prototype, optimized for modern CPUs with AVX2 support and multi-core architectures.

## Key Improvements
- **AVX2 Vectorization:** Processes 4 particles (double precision) or 8 particles (single precision) per SIMD instruction.
- **Symplectic Integrity:** 4th-order Yoshida Integrator for precise long-term tracking in circular lattices.
- **PIC/FFT Space Charge:** High-fidelity collective effects using FFTW3 2D Poisson solver.
- **High-Fidelity Physics Modules:**
    - **Field Map Element:** 3D trilinear interpolation for realistic magnetic/RF fields.
    - **Synchrotron Radiation:** Stochastic energy loss using vectorized Xorshift128+ PRNG.
    - **Collimator:** SIMD-masked physical apertures for particle loss diagnostics.
- **SoA Architecture:** Structure of Arrays (SoA) data layout for maximum cache efficiency and SIMD throughput.
- **OpenMP Scaling:** Parallelized lattice traversal across all available CPU cores.

## Prerequisites
- **Compiler:** GCC 9+, Clang 10+, or MSVC 2019+ (with AVX2 support).
- **Libraries:**
  - [FFTW3](https://www.fftw.org/) (Required for Space Charge).
  - OpenMP (Built-in with most modern compilers).
  - [Intel oneAPI (DPC++)](https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html) (Required for GPU/SYCL offloading).

## Building

### Linux / macOS (CPU only)
```bash
g++ -O3 -mavx2 -mfma -fopenmp main.cpp AcceleratorEngineAVX2.cpp PoissonSolver.cpp -o acc_sim -lfftw3 -lm
```

### Windows (PowerShell / MSVC)
```powershell
cl /O2 /arch:AVX2 /openmp main.cpp AcceleratorEngineAVX2.cpp PoissonSolver.cpp /Fe:acc_sim.exe /I path/to/fftw/include /link /LIBPATH:path/to/fftw/lib libfftw3-3.lib
```

### Intel oneAPI (GPU/SYCL Offload)
```bash
icpx -fsycl -O3 AcceleratorEngineSYCL.cpp -o acc_sim_gpu
```

## Usage

### C++ Console
The engine can be configured via `main.cpp`. 
```bash
./acc_sim
```

### Python Orchestration
Use the provided `accelerator_cpp_wrapper.py` for Python-to-C++ integration.
```python
from accelerator_cpp_wrapper import AcceleratorEngineCPP
engine = AcceleratorEngineCPP(particle_count=1000000)
engine.add_lattice_from_json("lattice.json")
engine.run(steps=100)
```

### Real-Time Dashboard
Start the Dash-based visualization server:
```bash
python accelerator_dashboard.py
```

## Leveraging Intel UHD 770 (Integrated GPU)

### 1. Compute Offload (SYCL)
The engine includes `AcceleratorEngineSYCL.hpp` which utilizes Intel oneAPI to offload tracking kernels directly to the UHD 770's execution units via Unified Shared Memory (USM).

### 2. Real-time Visualization
The Dash dashboard provides live phase-space plots ($x$-$px$, $y$-$py$, $z$-$delta$) and envelope diagnostics, polling data from the high-speed C++ backend.

## Performance Metrics
- **Throughput:** ~1-5 ns per particle per element (CPU-only).
- **Capacity:** Tested up to 10^7 particles.
- **Stability:** Yoshida 4th-order ensures energy conservation for >10^6 turns.
