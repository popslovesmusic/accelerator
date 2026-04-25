# Bifurcation / Continuation Analyzer (v1)

This tool formally maps the regime boundaries and stability onsets of the `acellorator` simulators. It performs dynamic parameter ramping and continuation analysis within a single long-running simulation to observe state transitions and hysteresis.

## Theoretical Basis

- **Bifurcation Analysis:** The study of changes in the qualitative structure of a system's behavior (e.g., from disordered to synchronized) as a parameter is varied.
- **Hysteresis:** The phenomenon where the state of a system depends on its history. This tool tests for "ratchet" effects by ramping parameters up and then back down.
- **Dynamic Continuation:** Unlike the Monte Carlo scanner, this tool keeps the exact system state as it shifts the parameter, revealing how established structures (like phase-locked domains) deform or break.

## Usage

Define a ramp protocol in a JSON config and run the runner:

```powershell
python bifurcation_runner.py --config configs/kuramoto_ramp.json --out outputs/kuramoto_bifurcation
```

## Configuration Guide

The JSON config expects:
1. `engine_module`: Path to the Python file containing the engine (e.g., `../kuramoto_sim_v1/kuramoto_engine.py`).
2. `engine_class`: The name of the class to instantiate (e.g., `KuramotoEngine`).
3. `base_config`: Base configuration JSON for the engine.
4. `ramp_params`:
   - `parameter`: The variable to vary (e.g., `K`).
   - `start`, `end`: The parameter range.
   - `steps`: Number of parameter increments.
   - `steps_per_plateau`: Simulation steps to wait at each parameter value for the system to settle.

## Outputs

- `bifurcation_trace.csv`: Time-series mapping the parameter value to the system metrics.
- `bifurcation_summary.json`: Identified critical transition points.
- `plots/`: Bifurcation diagrams showing observables vs. the driving parameter.
