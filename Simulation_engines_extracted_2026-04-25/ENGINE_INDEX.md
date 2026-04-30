# Simulation Engines (Extracted)

This directory is an engine-only extraction from:

`D:\projects\acellorator\Simulation`

Source engines live under:

`D:\projects\acellorator\Simulation\src\cpp`

Extracted to:

`D:\projects\acellorator\Simulation_engines_extracted_2026-04-25`

## What Was Extracted

- `src/cpp/` (all C++ engine sources and headers)
- `CMakeLists.txt` (builds D-ASE core + IGSOA GW core)
- `dase_cli/` (strict JSON CLI sources + example command JSON)
- FFTW headers/libs needed by the build:
  - `fftw3.h`
  - `libfftw3-3.lib`, `libfftw3-3.dll`, `libfftw3-3.def`

This extraction intentionally excludes most non-engine material from the full Simulation repo (web/backend/scripts/results/etc).

## Engine Families

### 0) UHD 770 / oneAPI Acceleration Layer

Purpose:
- Provide a guarded Intel UHD 770 target path for C++ engines without removing
  the existing AVX2/OpenMP CPU reference path.
- Report SYCL compile status, selected Intel GPU device, FP64 support, and FP32
  numeric probe results.

Key files:
- `src/cpp/uhd770_runtime.h`
- `src/cpp/uhd770_device_probe.cpp`

Build target:
- `uhd770_device_probe`

CLI support:
- `get_capabilities` now reports `gpu_features`.
- `get_acceleration_status` reports the UHD 770/SYCL state and can run an FP32
  vector-math probe with `{"run_probe": true}`.

Scientific policy:
- UHD 770 is treated as an FP32-first production target.
- CPU AVX2/OpenMP remains the FP64/reference path for drift checks.
- Empirical claims still require recoverable output and CPU/GPU drift reporting.
- The D-ASE Phase4B mission path now exposes a UHD 770 FP32 backend through
  `run_mission` using `{"backend":"uhd770","drift_check":true}`.

### 1) D-ASE Analog Engine (AVX2 + UHD 770-ready diagnostics)

Purpose:
- High-performance analog node/cellular signal simulation (AVX2 + OpenMP + FFTW).
- The current extracted implementation remains CPU AVX2/OpenMP for its mission loop,
  with UHD 770/SYCL device detection and probe infrastructure now wired into the
  build and CLI. Engine-specific kernel migration should be done behind CPU/GPU
  parity tests rather than by replacing the AVX2 reference path.

Key files:
- `src/cpp/analog_universal_node_engine_avx2.h`
- `src/cpp/analog_universal_node_engine_avx2.cpp`
- `src/cpp/dase_capi.h`
- `src/cpp/dase_capi.cpp`
- `src/cpp/python_bindings.cpp` (pybind11 bindings; not built by the provided CMake)
- `src/cpp/fftw_wisdom_cache.hpp`

Main types / APIs:
- `AnalogUniversalNodeAVX2`
- `AnalogCellularEngineAVX2`
- C API entrypoints in `dase_capi.h` (handle-based FFI intended for Julia/Rust/etc)

Build notes:
- The provided `CMakeLists.txt` builds this as `dase_core` and several `dase_engine_*` shared libraries (Julia DLLs) by default.

### 2) IGSOA Complex Lattice Engines (1D / 2D / 3D)

Purpose:
- Complex-valued informational/quantum-like lattice simulation with complex `psi`, real `phi`, density `F=|psi|^2`, phase, and entropy-rate diagnostics.

Key files:
- `src/cpp/igsoa_complex_node.h` (node + config types)
- `src/cpp/igsoa_complex_engine.h` (1D/unstructured engine)
- `src/cpp/igsoa_physics.h` (1D physics)
- `src/cpp/igsoa_complex_engine_2d.h`, `src/cpp/igsoa_physics_2d.h`, `src/cpp/igsoa_state_init_2d.h`
- `src/cpp/igsoa_complex_engine_3d.h`, `src/cpp/igsoa_physics_3d.h`, `src/cpp/igsoa_state_init_3d.h`
- `src/cpp/igsoa_capi.h`, `src/cpp/igsoa_capi.cpp` (1D C API)
- `src/cpp/igsoa_capi_2d.h`, `src/cpp/igsoa_capi_2d.cpp` (2D C API)

Support modules:
- `src/cpp/spatial_hash.h`, `src/cpp/kernel_cache.h`, `src/cpp/neighbor_cache.h` (neighbor acceleration utilities)
- `src/cpp/igsoa_status.h` (status/error codes)
- `src/cpp/utils/logger.h`, `src/cpp/utils/logger.cpp`

Build notes:
- These are mostly header-based engines/physics (not currently built as a library target in the provided `CMakeLists.txt`).

### 3) SATP+Higgs Coupled Field Engines (1D / 2D / 3D)

Purpose:
- Coupled wave-equation evolution of `phi` (scale/SATP field) and `h` (Higgs-like field with SSB), using velocity Verlet integrators.

Key files:
- `src/cpp/satp_higgs_engine_1d.h`, `src/cpp/satp_higgs_physics_1d.h`, `src/cpp/satp_higgs_state_init_1d.h`
- `src/cpp/satp_higgs_engine_2d.h`, `src/cpp/satp_higgs_physics_2d.h`, `src/cpp/satp_higgs_state_init_2d.h`
- `src/cpp/satp_higgs_engine_3d.h`, `src/cpp/satp_higgs_physics_3d.h`, `src/cpp/satp_higgs_state_init_3d.h`

Build notes:
- Header-based implementation; not currently wired into the provided `CMakeLists.txt` as build targets.

### 4) IGSOA Gravitational Wave Engine (Core)

Purpose:
- 3D symmetry/asymmetry field evolution, fractional-memory solver, binary merger source generation, projection operators, and echo generation.

Key files:
- `src/cpp/igsoa_gw_engine/core/symmetry_field.h`, `src/cpp/igsoa_gw_engine/core/symmetry_field.cpp`
- `src/cpp/igsoa_gw_engine/core/fractional_solver.h`, `src/cpp/igsoa_gw_engine/core/fractional_solver.cpp`
- `src/cpp/igsoa_gw_engine/core/source_manager.h`, `src/cpp/igsoa_gw_engine/core/source_manager.cpp`
- `src/cpp/igsoa_gw_engine/core/projection_operators.h`, `src/cpp/igsoa_gw_engine/core/projection_operators.cpp`
- `src/cpp/igsoa_gw_engine/core/echo_generator.h`, `src/cpp/igsoa_gw_engine/core/echo_generator.cpp`
- `src/cpp/utils/logger.*`

Build notes:
- The provided `CMakeLists.txt` builds this as `igsoa_gw_core` (static library) and links against FFTW and `igsoa_utils`.

## Build Quickstart (CMake)

From `D:\projects\acellorator\Simulation_engines_extracted_2026-04-25`:

```powershell
cmake -S . -B build -DDASE_BUILD_TESTS=OFF -DDASE_BUILD_PYTHON=OFF
cmake --build build --config Release
```

Notes:
- FFTW is expected in this directory root (already copied here).
- Python bindings are present as source (`src/cpp/python_bindings.cpp`) but the provided `CMakeLists.txt` does not currently build them as a target.

## UHD 770 Build Quickstart

Use Intel oneAPI and configure with the IntelLLVM compiler so `-fsycl` is active:

```powershell
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
cmake -S . -B build_uhd770 -G Ninja -DCMAKE_CXX_COMPILER=icx -DCMAKE_BUILD_TYPE=Release -DDASE_ENABLE_UHD770_SYCL=ON -DDASE_UHD770_FP32_DEFAULT=ON -DDASE_BUILD_JSON_CLI=ON -DDASE_BUILD_PYTHON=OFF -DDASE_BUILD_TESTS=OFF
cmake --build build_uhd770 --target uhd770_device_probe
.\build_uhd770\uhd770_device_probe.exe --out outputs\uhd770\device_probe\report.json
```

If CMake is configured with MSVC `cl`, the code still compiles, but the SYCL
runtime reports CPU fallback. That is intentional: use `icx`/`icpx` for actual
UHD 770 kernels.

Helper scripts live under `scripts/`:

```powershell
.\scripts\build_uhd770_probe.bat
.\scripts\build_uhd770_cli.bat
.\scripts\run_uhd770_smoke.bat
```

Generated binaries go to `bin/uhd770/`. Recoverable run outputs go to
`outputs/uhd770/<run-name>/`.

## Strict JSON CLI

Purpose:
- Headless, line-delimited JSON command interface for creating engines, running missions, extracting state, and performing analysis routing.

Key files:
- `dase_cli/src/main.cpp` (reads JSON commands from stdin, outputs JSON responses)
- `dase_cli/src/command_router.*`
- `dase_cli/src/engine_manager.*` (loads `dase_engine_phase4b.dll` / `dase_engine.dll`, and also hosts IGSOA + SATP/Higgs header-only engines)
- `dase_cli/src/analysis_router.*`, `dase_cli/src/engine_fft_analysis.*`, `dase_cli/src/python_bridge.*`

Build target:
- `dase_cli_json`

UHD 770 commands:

```json
{"command":"get_acceleration_status","params":{"run_probe":true}}
```

Example build:

```powershell
cmake -S . -B build -DDASE_BUILD_JSON_CLI=ON
cmake --build build --config Release --target dase_cli_json
```

