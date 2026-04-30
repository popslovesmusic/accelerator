# Symplectic SIM C++ (v2.3)

SYCL-ready C++ port of the nonlinear pendulum symplectic simulator.

## Scientific Rigor

- Uses a second-order leapfrog / velocity-Verlet update.
- Runs matched FP32 and FP64 trajectories from the same deterministic initial state.
- Emits energy drift, relative energy drift, and FP32-vs-FP64 precision drift.
- Includes a zero-step falsification check: with no integration steps, energy drift must be zero.

## Usage

```powershell
.\symplectic_sim_v1_cpp\build_and_run.bat
```

Outputs are written to `symplectic_sim_v1_cpp/outputs/v2p3_report.json` and
`symplectic_sim_v1_cpp/outputs/metrics.csv`.
