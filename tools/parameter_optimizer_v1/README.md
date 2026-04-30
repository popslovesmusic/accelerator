# Constraint / Parameter Optimizer (v1)

This tool solves inverse problems by actively searching for simulation parameters that maximize (or minimize) target metrics. It wraps the `acellorator` engines and uses gradient-free optimization to discover optimal regimes.

## Theoretical Basis

- **Inverse Problem Solving:** Moving from a desired outcome (e.g., maximum coherence) to the necessary parameter configuration.
- **Black-Box Optimization:** Since simulations are non-differentiable and noisy, we use methods like Nelder-Mead or Random Search.
- **Regime Discovery:** Automates the search for exact conditions that trigger "corridors," "shelves," or "locked" states.

## Usage

Define an optimization problem in a JSON config and run the runner:

```powershell
python optimize_runner.py --config configs/opt_kuramoto.json --out outputs/kuramoto_opt
```

## Configuration Guide

The JSON config expects:
1. `target_script`: Path to the simulator's `sim.py`.
2. `base_config`: Path to the base JSON config.
3. `target_metric`: The metric to maximize (from `summary.json`), e.g., `final_metrics.order_parameter`.
4. `method`: `random` or `nelder-mead`.
5. `max_evals`: Maximum number of simulation runs.
6. `search_params`: Dictionary of parameters to optimize with `[min, max]` bounds.

## Outputs

- `optimization_trace.csv`: History of evaluated parameters and their scores.
- `best_config.json`: The discovered configuration that yielded the best metric.
- `summary.json`: Optimization results and final metrics.
