# Rerun Software Staging Area

This directory holds the isolated rerun runtime.

- `src/` is a staged copy of the reusable legacy root `src/`.
- `sitecustomize.py` forces new Python interpreters to import the staged `src/` package instead of any editable-install shadow copy elsewhere on the machine.
- `software_manifest.json` records exactly which files were copied.
- `rerun_v23.tools.batch_wrapper` should execute against this directory, not the legacy root workspace.
- `src/build_level2_native.ps1` rebuilds the staged `_level2_native` extension in place for the canonical native PDE engine.
- `src/native_parity.py` checks that the staged Python fallback remains numerically aligned with the native PDE reference.
- `src/pde_solver.py` and `src/level2_pde_engine.cpp` now support `phase_expression = "standard"`, `phase_expression = "I_phi_inverted"`, `phase_expression = "I_phi_v2_basis_inverse"`, and `phase_expression = "I_phi_v3_delta_sigma_rho"`.
- `src/pde_solver.py` also now supports the Python-only `phase_expression = "I_phi_v4_dsr"` branch with event-gated seed updates driven by `src/dsr_geometry.py`.
- `src/phase_delta_report.py` compares separate standard and inverted batch outputs and emits a paired metric delta CSV.
- `src/delta_sigma_calibration.py` resolves frozen `Delta/Sigma` calibration from `configs/sim18_v3/delta_sigma_calibration_v1.json` before the relational runtime executes.
- `src/dsr_seed_floor_harness.py` and `src/dsr_delta_only_harness.py` provide the local pre-implementation DSR gates before any governed runtime staging.

Refresh this staging area with:

```powershell
python -m rerun_v23.tools.software_sync --project-root G:\MPF\orientation\level2 --software-root G:\MPF\orientation\level2\rerun_v23\software --clean
```

The root `src/` remains reference material and source provenance. The staged copy is the clean execution environment. Within this staged runtime, the native C++ PDE backend is the primary execution engine and the Python PDE path is retained as fallback and regression coverage.

When running staged Python entrypoints directly, set:

```powershell
$env:PYTHONPATH='G:\MPF\orientation\level2\rerun_v23\software'
```

This keeps the staged `src/` package ahead of any older editable-install shadow copy elsewhere on the machine.

To rebuild the staged native backend:

```powershell
powershell -ExecutionPolicy Bypass -File G:\MPF\orientation\level2\rerun_v23\software\src\build_level2_native.ps1
```

For governed rerun batches, prefer the native backend explicitly:

```powershell
python -m rerun_v23.tools.batch_wrapper --config <config.json> --batch-id <batch_id> --backend native
```

To run a fast staged parity smoke check:

```powershell
$env:PYTHONPATH='G:\MPF\orientation\level2\rerun_v23\software'
python -m src.native_parity --config G:\MPF\orientation\level2\rerun_v23\configs\anchors\ss2_anchor_v23.json --t-final 10 --max-run-specs 1 --max-seeds 1 --max-ics 1
```

To compare separate standard and inverted sim18 batches after execution:

```powershell
$env:PYTHONPATH='G:\MPF\orientation\level2\rerun_v23\software'
python -m src.phase_delta_report --standard-batch <standard_batch_or_outputs_dir> --inverted-batch <inverted_batch_or_outputs_dir> --output <delta_report.csv>
```
