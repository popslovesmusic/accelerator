# Monte Carlo Ensemble C++ (v2.3)

C++ orchestration port for parameter sweeps.

This runner is intentionally simulator-agnostic. It consumes a JSON config with an executable
command template and writes generated trial configs plus an `ensemble_results.csv` manifest.
It does not invoke Python.

## Config Shape

```json
{
  "trials": 10,
  "seed": 123,
  "command_template": "target.exe --config {config} --out {out}",
  "base_config": {"steps": 1000},
  "scan_params": {
    "K": {"type": "uniform", "min": 0.0, "max": 2.0},
    "mode": {"type": "choice", "values": ["a", "b"]}
  }
}
```

## Usage

```powershell
.\mc_ensemble_sim_v1_cpp\build_and_run.bat
```
