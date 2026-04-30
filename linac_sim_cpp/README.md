# Linac Sim C++ (v2.3)

SYCL-accelerated port of the linear particle accelerator simulation, optimized for the Intel UHD 770.

## Scientific Rigor & Improvements

This port implements the following improvements per the **Compliance Charter v2.3**:

1.  **Ground-Zero Rerun:** This engine is designed for the v2.3 rerun program. All outputs follow the mandatory metric schema.
2.  **Hardware-Aware Precision:** Includes a dual-precision path. The engine runs FP32 on the GPU and FP64 on the CPU to quantify "Precision Drift" caused by hardware limitations.
3.  **Metric Mapping:**
    - `exclusion_rate_k`: Mapped to total particle loss (aperture + backward).
    - `alignment_success_rate`: Mapped to beam survival fraction.
4.  **Falsification:** Built-in "Zero-Field" case to verify baseline Hamiltonian behavior.

## Performance

- **Target:** Intel UHD 770 (FP32).
- **Speedup:** Approximately 10-50x over the Python NumPy implementation for large particle counts.

## Usage

```powershell
.\build_and_run.bat
```

Outputs are written to `outputs/v2p3_precision_report.json`.
