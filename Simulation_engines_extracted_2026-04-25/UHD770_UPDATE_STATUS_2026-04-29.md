# UHD 770 Update Status (2026-04-29)

## Scope

This update applies to the extracted C++ engine package at
`Simulation_engines_extracted_2026-04-25`.

## Implemented

- Added guarded oneAPI/SYCL runtime support in `src/cpp/uhd770_runtime.h`.
- Added `uhd770_device_probe` for Intel GPU detection and FP32 numeric validation.
- Added CMake options:
  - `DASE_ENABLE_UHD770_SYCL`
  - `DASE_UHD770_FP32_DEFAULT`
- Added CLI command:
  - `get_acceleration_status`
- Added D-ASE analog mission backend selection:
  - `run_mission` accepts `"backend": "uhd770"` for the Phase4B engine.
  - `run_mission` accepts `"drift_check": true` to run a matched CPU reference
    and report CPU/GPU drift.
- Added exported C API symbols:
  - `dase_run_mission_optimized_uhd770`
  - `dase_get_uhd770_metrics`
- Updated `get_capabilities` to report GPU/SYCL/UHD 770 status.
- Made the CLI tolerate a missing legacy D-ASE DLL so diagnostics and header-only
  engines can still run.
- Added direct oneAPI build scripts:
  - `scripts/build_uhd770_probe.bat`
  - `scripts/build_uhd770_cli.bat`
  - `scripts/run_uhd770_smoke.bat`
- Verified the CMake path with a separate `build_uhd770` directory using IntelLLVM
  and Ninja.
- Standardized generated artifact homes:
  - manually-built binaries: `bin/uhd770/`
  - CMake products: `build_uhd770/`
  - recoverable run reports: `outputs/uhd770/<run-name>/`

## Verified Locally

Built with Intel oneAPI through both direct `icpx -fsycl` and CMake:

```powershell
cmake -S . -B build_uhd770 -G Ninja `
  -DCMAKE_CXX_COMPILER=icx `
  -DCMAKE_BUILD_TYPE=Release `
  -DDASE_ENABLE_UHD770_SYCL=ON `
  -DDASE_UHD770_FP32_DEFAULT=ON `
  -DDASE_BUILD_JSON_CLI=ON `
  -DDASE_BUILD_PYTHON=OFF `
  -DDASE_BUILD_TESTS=OFF
cmake --build build_uhd770 --target uhd770_device_probe
cmake --build build_uhd770 --target dase_cli_json
.\build_uhd770\uhd770_device_probe.exe --out outputs\uhd770\device_probe\report.json
```

Verified selected device:

```json
{
  "selected_device": "Intel(R) UHD Graphics 770",
  "backend": "oneAPI_SYCL",
  "sycl_compiled": true,
  "gpu_available": true,
  "uhd770_likely": true,
  "fp64_supported": false,
  "probe": {
    "name": "fp32_vector_math",
    "passed": true,
    "n": 1048576,
    "max_abs_error": 1.6020161908159025e-7
  }
}
```

CMake-built CLI verification:

```json
{
  "command": "get_acceleration_status",
  "status": "success",
  "result": {
    "selected_device": "Intel(R) UHD Graphics 770",
    "backend": "oneAPI_SYCL",
    "gpu_available": true,
    "uhd770_likely": true,
    "fp32_default": true,
    "probe": {
      "passed": true,
      "n": 1048576
    }
  }
}
```

D-ASE analog Phase4B UHD 770 mission verification:

```json
{
  "command": "run_mission",
  "status": "success",
  "result": {
    "backend_requested": "uhd770",
    "steps_completed": 64,
    "total_operations": 1048576,
    "uhd770": {
      "used": true,
      "drift_check_passed": true,
      "max_abs_drift": 1.0121143246416553e-9,
      "mean_abs_drift": 1.0121143246416553e-9
    }
  }
}
```

## Scientific Rigor Policy

- UHD 770 is now treated as an FP32-first GPU target.
- AVX2/OpenMP remains the CPU reference path for correctness and drift checks.
- A C++ engine result should not be promoted as verified unless the run emits
  recoverable output and reports CPU/GPU precision drift where applicable.

## Remaining Work

- Continue migrating individual heavy loops from AVX2/OpenMP to SYCL kernels
  engine by engine. The first Phase4B analog mission path now has a UHD 770
  FP32 kernel with CPU drift reporting.
- Add per-engine CPU/GPU regression tests before retiring the CPU reference path.
- Replace FFTW-dependent spectral kernels with oneMKL/oneAPI equivalents only after
  matching FFTW outputs on fixed test fields.
