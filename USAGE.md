# USAGE: Acellorator Research Ecosystem

This document provides operational instructions for using the rectified and governed research repository.

## 📁 Key Directories

- **`tools/`**: Primary location for all simulation engines.
  - Subdirectories: `agent_based_sim_v1/`, `symplectic_sim_v1_cpp/`, etc.
  - Each tool has a `validation/` directory with C4 artifacts.
- **`registry/`**: Central governing manifests.
  - `tool_manifest.json`: Master tool registry.
  - `validation_index.json`: Global validation status.
  - `compliance_charter_v2_3.json`: Mathematical and provenance authority.
- **`registry/math/` + `docs/math/`**: Math core registries + codex (interpretation and governance; not physics proof).
- **`configs/`**: Standardized configurations.
  - `multi_runs/`: Orchestration configs for `multi_sim_runner.py`.
  - `examples/`: Tool-specific reference configs.
- **`outputs/`**: Recoverable evidence.
  - `runs/`: Organized by Run ID.
  - `audits/`: Gap matrices and project metadata.

## 🚀 Running Simulations

### 1. Governed Multi-Sim Runner
Always prefer using the orchestrated runner for multi-tool or multi-seed campaigns:
```bash
python scripts/multi_sim_runner.py --config configs/multi_runs/example_multi_sim_run.json
```
- **Provenance:** Automatically captures Git commit and config hashes.
- **UQ:** Grouping by seed and calculating statistics (Mean, Stdev, CI).

### 2. Numerical Validation
Run convergence sweeps for PDE/ODE tools:
```bash
cmd /c scripts/run_convergence_governed.bat --tool <name> --base-config <path> --param <name> --values <vals>
```

### 3. Functional Equivalence
Verify Python/C++ parity:
```bash
cmd /c scripts/run_regression_governed.bat --tool-a <py_tool> --tool-b <cpp_tool> --config <config>
```

## 📊 Checking Certification Status

- Review the **Scientific Rigor Report**: `docs/reports/TOOL_SCIENTIFIC_RIGOR_REPORT_2026-04-30.md`.
- Check tool-local manifests: `tools/<name>/validation/certification_manifest.json`.

## ⚖️ Governance Mandate

1. **Claim Humility:** Always begin results with: "Within these models..."
2. **Requirement of Equivalence:** C++ performance must match Python logic.
3. **Model Inclusion:** All reports and writing MUST explicitly include the **model** being tested or cited.
