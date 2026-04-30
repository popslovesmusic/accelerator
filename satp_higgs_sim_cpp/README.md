# SATP+Higgs 2D SIM C++ (v2.3)

SYCL-accelerated port of the coupled field simulation (Scale field + Higgs field with SSB), optimized for the Intel UHD 770.

## Scientific Rigor & Improvements

This port implements the following improvements per the **Compliance Charter v2.3**:

1.  **Ground-Zero Rerun:** This engine is part of the v2.3 rerun program.
2.  **Hardware-Aware Precision:** Includes a dual-precision path (FP32 GPU vs FP64 CPU).
3.  **Metric Mapping:**
    - `phi_rms`: Intensity of the scale field perturbation.
    - `higgs_rms`: Deviation from the Higgs VEV baseline.
    - `alignment_success_rate`: Fidelity of the GPU result compared to the CPU baseline.
4.  **Falsification:** Built-in "Decoupled Fields" case (setting $\lambda=0$) to verify that the field interaction is correctly modeled.

## Performance

- **Target:** Intel UHD 770 (FP32).
- **Speedup:** Approximately 10-20x over the header-only CPU implementation for larger grids.

## Usage

```powershell
.\build_and_run.bat
```

Outputs are written to `outputs/v2p3_report.json`.
