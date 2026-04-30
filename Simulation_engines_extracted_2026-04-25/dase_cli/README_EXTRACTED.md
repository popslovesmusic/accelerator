# DASE Strict JSON CLI (Extracted)

This directory contains the strict JSON CLI that was extracted alongside the simulation engines.

The CLI reads line-delimited JSON commands from stdin and writes JSON responses to stdout.

## Build (From Extracted Root)

From `D:\projects\acellorator\Simulation_engines_extracted_2026-04-25`:

```powershell
cmake -S . -B build -DDASE_BUILD_JSON_CLI=ON -DDASE_BUILD_JULIA_DLLS=ON
cmake --build build --config Release --target dase_cli_json
```

Notes:
- With `DASE_BUILD_JULIA_DLLS=ON`, the build produces `dase_engine_phase4b.dll` / `dase_engine.dll`.
- The extracted root `CMakeLists.txt` copies the engine DLL(s) and `libfftw3-3.dll` next to `dase_cli_json.exe` so it can load them at runtime.

## Run

Example:

```powershell
.\build\Release\dase_cli_json.exe
```

You can also use `--describe`:

```powershell
.\build\Release\dase_cli_json.exe --describe igsoa_complex
```

Example command JSON files in this folder:

- `examples.json`
- `quick_test_commands.json`


