# Reaction-Diffusion Moving Boundary SIM C++ (v2.3)

SYCL-accelerated port of the Reaction-Diffusion simulation with dynamic topological boundaries, optimized for the Intel UHD 770.

## Scientific Rigor & Improvements

This port implements the following improvements per the **Compliance Charter v2.3**:

1.  **Ground-Zero Rerun:** This engine is designed for the v2.3 rerun program. All outputs follow the mandatory metric schema.
2.  **Hardware-Aware Precision:** Includes a dual-precision path. The engine runs FP32 on the GPU and FP64 on the CPU to quantify "Precision Drift".
3.  **Metric Mapping:**
    - `active_area`: Total domain $D$ occupancy.
    - `total_signal`: Integral of the signal $S$.
    - `exclusion_rate_k`: Mapped to the ratio of area under high-decay conditions vs baseline.
4.  **Falsification:** Built-in "High Signal Decay" case to verify that domain growth is signal-dependent.

## Performance

- **Target:** Intel UHD 770 (FP32).
- **Speedup:** Approximately 20-100x over the Python NumPy implementation for large grids.

## Usage

```powershell
.\build_and_run.bat
```

Outputs are written to `outputs/v2p3_report.json`.
