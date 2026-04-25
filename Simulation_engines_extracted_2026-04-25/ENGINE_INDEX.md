# Simulation Engines (Extracted)

This directory is an engine-only extraction from:

`D:\acellorator\Simulation`

Source engines live under:

`D:\acellorator\Simulation\src\cpp`

Extracted to:

`D:\acellorator\Simulation_engines_extracted_2026-04-25`

## What Was Extracted

- `src/cpp/` (all C++ engine sources and headers)
- `CMakeLists.txt` (builds D-ASE core + IGSOA GW core)
- `dase_cli/` (strict JSON CLI sources + example command JSON)
- FFTW headers/libs needed by the build:
  - `fftw3.h`
  - `libfftw3-3.lib`, `libfftw3-3.dll`, `libfftw3-3.def`

This extraction intentionally excludes most non-engine material from the full Simulation repo (web/backend/scripts/results/etc).

## Engine Families

### 1) D-ASE Analog Engine (AVX2)

Purpose:
- High-performance analog node/cellular signal simulation (AVX2 + OpenMP + FFTW).

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

From `D:\acellorator\Simulation_engines_extracted_2026-04-25`:

```powershell
cmake -S . -B build -DDASE_BUILD_TESTS=OFF -DDASE_BUILD_PYTHON=OFF
cmake --build build --config Release
```

Notes:
- FFTW is expected in this directory root (already copied here).
- Python bindings are present as source (`src/cpp/python_bindings.cpp`) but the provided `CMakeLists.txt` does not currently build them as a target.

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

Example build:

```powershell
cmake -S . -B build -DDASE_BUILD_JSON_CLI=ON
cmake --build build --config Release --target dase_cli_json
```
