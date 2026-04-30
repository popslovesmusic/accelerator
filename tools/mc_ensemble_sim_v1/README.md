# Monte Carlo Ensemble Simulator (v1)

This tool is a meta-orchestrator designed to map the parameter space of other simulators in the `acellorator` ecosystem. It runs randomized trials in parallel to identify **regime boundaries** and **probability surfaces**.

## Theoretical Basis

- **Ensemble Mapping:** Instead of a single trajectory, the model explores the statistical ensemble of outcomes across a range of parameters.
- **Empirical Regime Boundaries:** Uses many trials to find critical transition points (e.g., the onset of synchronization or structural collapse).
- **Robustness Analysis:** Tests how sensitive a regime (like SS3) is to noise or parameter variation.

## Usage

```powershell
python mc_runner.py --config configs/sweep_kuramoto.json --out outputs/kuramoto_sweep
```

## Scan Configuration

The tool expects a JSON file specifying:
1. `target_script`: Path to the simulator's `sim.py`.
2. `base_config`: Path to the base JSON for that simulator.
3. `trials`: Number of Monte Carlo runs.
4. `scan_params`: Dictionary of parameters to vary, with sampling rules:
   - `{"type": "uniform", "min": 0, "max": 5}`
   - `{"type": "choice", "values": [0.1, 0.5, 1.0]}`

## Outputs

- `ensemble_results.csv`: A flattened table containing all input parameters and final metrics for every trial.
- `regime_map.png`: A scatter plot mapping the scanned parameters against output metrics (if Matplotlib is installed).
