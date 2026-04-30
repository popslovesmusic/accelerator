# Stochastic SIM C++ (v2.3)

SYCL-accelerated port of the Stochastic Threshold simulation, optimized for the Intel UHD 770.

## Scientific Rigor & Improvements

This port implements the following improvements per the **Compliance Charter v2.3**:

1.  **Ground-Zero Rerun:** This engine is designed for the v2.3 rerun program. All outputs follow the mandatory metric schema.
2.  **Hardware-Aware Precision:** Includes a dual-precision path. The engine runs FP32 on the GPU and FP64 on the CPU to quantify "Precision Drift".
3.  **Metric Mapping:**
    - `mean_x`: Average position of particles.
    - `crossing_fraction`: Fraction of particles that have crossed the threshold (`x_thresh`).
    - `exclusion_rate_k`: Mapped as `1.0 - crossing_fraction`.
4.  **Falsification:** Built-in "Zero Noise" case to verify that without stochastic driving, no particles cross the threshold.

## Performance

- **Target:** Intel UHD 770 (FP32).
- **Speedup:** Approximately 10-20x over the Python implementation for large particle counts (100k+).

## Usage

```powershell
.\build_and_run.bat
```

Outputs are written to `outputs/v2p3_report.json`.
