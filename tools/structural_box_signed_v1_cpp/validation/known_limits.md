## Known limits (tool-local)

- Runtime dependency: `box_sim.exe` requires Intel oneAPI SYCL/DPC++ runtime DLLs. In a fresh PowerShell, run the Intel oneAPI `setvars.bat` (if installed) to populate `PATH` before executing.
- Device selection: the executable uses SYCL `default_selector` for GPU and `cpu_selector` for CPU; device availability differs by machine.
- Provenance: `summary.json` includes `config` and `run_date` fields, but does not currently embed a `source_commit` or `config_hash` unless launched via `sim_governed.py` (which writes `run_metadata.json`).

