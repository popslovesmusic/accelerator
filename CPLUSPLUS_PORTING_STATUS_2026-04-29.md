# C++ Porting Status (2026-04-29)

## Purpose

This checkpoint supports retirement/archive of Python implementations by tracking C++
counterparts, executable status, and scientific-rigor upgrades.

## Newly Added Ports

| Python component | C++ component | Status | Rigor additions |
| --- | --- | --- | --- |
| `symplectic_sim_v1` | `symplectic_sim_v1_cpp` | Builds and runs | FP32/FP64 comparison, energy drift, zero-step falsification |
| `spectral_analysis_v1` | `spectral_analysis_v1_cpp` | Builds and runs | Temporal DFT, spatial DFT/radial modes, known-mode controls |
| `tda_module_v1` | `tda_module_v1_cpp` | Builds and runs | Spatial Betti-0 controls and network connected-component control |
| `mc_ensemble_sim_v1` | `mc_ensemble_sim_v1_cpp` | Builds and runs | Non-Python executable command templates, recoverable trial manifests |
| `parameter_optimizer_v1` | `parameter_optimizer_v1_cpp` | Builds and runs | Deterministic random search, recoverable traces, JSON metric-path extraction |

## Existing C++ Ports Now Manifest-Registered

| Component | C++ directory |
| --- | --- |
| Linear accelerator | `linac_sim_cpp` |
| Stochastic threshold | `stochastic_sim_cpp` |
| Reaction-diffusion moving boundary | `rd_sim_cpp` |
| Structural box | `structural_box_sim_cpp` |

## Build Verification

The following were built with Intel oneAPI `icpx -fsycl` through their
`build_and_run.bat` scripts:

- `symplectic_sim_v1_cpp`
- `spectral_analysis_v1_cpp`
- `tda_module_v1_cpp`
- `mc_ensemble_sim_v1_cpp`
- `parameter_optimizer_v1_cpp`

Built-in controls passed for:

- `symplectic_sim_v1_cpp`: zero-step energy invariance
- `spectral_analysis_v1_cpp`: known temporal frequency and known spatial wavenumber
- `tda_module_v1_cpp`: empty/single/two spatial components and two network components

Additional root-output checks passed:

- `stochastic_sim_cpp`: report written to `outputs/stochastic_sim_cpp/v2p3_report.json`
- `rd_sim_cpp`: report written to `outputs/rd_sim_cpp/v2p3_report.json`
- `scripts/run_cpp_smoke.ps1`: logs and summary written to `outputs/cpp_smoke/`

## Root Output Convention

New root-level C++ runs should write recoverable artifacts under:

```text
outputs/<engine-or-program>/<run-name-or-report-files>
```

The newly added C++ ports and the audited UHD/SYCL report writers now follow this
root-output convention. Older engine-local `outputs/` directories may still contain
prior artifacts and should be preserved for provenance unless deliberately archived.

## Current Limits

- `spectral_analysis_v1_cpp` uses direct DFT for portability and rigor controls. For very
  large grids or long signals, replace with oneMKL FFT or another vetted C++ FFT backend.
- `parameter_optimizer_v1_cpp` implements deterministic random search. It does not yet
  reproduce the Python Nelder-Mead path.
- `mc_ensemble_sim_v1_cpp` records trial generation and command status. Cross-run metric
  aggregation should be extended per target simulator schema when Python is fully archived.
- Several existing C++ ports are SYCL-oriented but not all have been audited for full
  charter v2.3 schema completeness.

## Archive Guidance

Python code can be archived in phases:

1. Archive analysis tools after confirming downstream scripts use the new C++ CLIs.
2. Archive simulators only after matching a representative Python/C++ regression run.
3. Keep generated recoverable outputs and configs; do not overwrite default configs.
