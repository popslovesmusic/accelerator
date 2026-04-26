# Information Metrics Module (SYCL Upgraded)

This module provides high-performance information-theoretic metrics calculation using Intel oneAPI (SYCL) to offload heavy computations to the Intel UHD 770 GPU.

## Ported Metrics
- **Shannon Entropy:** Computed via GPU-accelerated atomic histogramming.
- **Mutual Information:** Computed via GPU-accelerated 2D joint histogramming.
- **Complexity:** Compression-based complexity (CPU-side).

## Key Improvements
- **Single-Precision Optimization:** Kernels are adapted for FP32 to ensure compatibility with integrated Intel GPUs (UHD 770).
- **Atomic Histogramming:** Uses SYCL `atomic_ref` for efficient parallel binning.
- **Python Integration:** Includes a `ctypes` wrapper for seamless use in existing analysis workflows.

## Build Instructions
Use the provided `build_and_run.bat` to compile the C++ benchmark and the shared library:
```batch
build_and_run.bat
```
To compile the DLL specifically for Python:
```batch
icpx -fsycl -O3 -shared metrics_capi.cpp -o metrics_engine.dll
```

## Usage
### Python
```python
from metrics_cpp_wrapper import MetricsEngineCPP
engine = MetricsEngineCPP()
entropy = engine.compute_entropy(data, bins=100)
mi = engine.compute_mutual_information(x, y, bins=100)
```

### Command Line Analysis
```bash
python analyze_info.py --dir path/to/simulation/output
```

## Performance
Tested with 1,000,000 samples:
- **Histogramming:** ~0.5ms on UHD 770.
- **Total Entropy calc:** ~1.2ms including data transfer and host-side probability normalization.
