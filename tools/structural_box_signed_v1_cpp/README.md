# Structural Box SIM C++ (v2.3)

SYCL-accelerated port of the Structural Box simulation, testing Identity, Stability, and Admissibility Margins. Optimized for the Intel UHD 770.

## Scientific Rigor & Improvements

This port implements the following improvements per the **Compliance Charter v2.3**:

1.  **Ground-Zero Rerun:** This engine is designed for the v2.3 rerun program. All outputs follow the mandatory metric schema.
2.  **Hardware-Aware Precision:** Includes a dual-precision path. The engine runs FP32 on the GPU and FP64 on the CPU to quantify "Precision Drift".
3.  **Metric Mapping:**
    - `epsilon_max`: Peak identity intensity.
    - `epsilon_active_fraction`: Fraction of space where identity is sustained above the threshold.
    - `alignment_success_rate`: Mapped to `epsilon_active_fraction`.
    - `exclusion_rate_k`: Mapped as `1.0 - epsilon_active_fraction`.
4.  **Falsification:** Built-in "Zero Mismatch (s=0)" case to test if identity can be sustained purely through internal dynamics (residue-coupling) without external driving.

## Performance

- **Target:** Intel UHD 770 (FP32).
- **Speedup:** Approximately 50-150x over the Python implementation for large grids (512+).

## Usage & Requirements

This tool depends on Intel oneAPI SYCL/DPC++ runtime components. If `box_sim.exe` fails immediately with an error code like `-1073741515` (`0xC0000135`), it usually indicates missing runtime DLLs on `PATH` (often resolved by running the Intel oneAPI `setvars.bat` in the same shell session).

### Usage (direct)

```powershell
.\box_sim.exe --out outputs\runs\smoke_001
```

Optional config:

```powershell
.\box_sim.exe --config configs\example.json --out outputs\runs\cfg_001
```

### Usage (governed launcher)

```powershell
python .\sim_governed.py --config .\configs\example.json --out .\outputs\runs\governed_001
```

Outputs are written to `<out_dir>/summary.json`.
