# Parameter Optimizer C++ (v2.3)

C++ port of the gradient-free parameter optimizer.

The runner uses deterministic random search over bounded parameters and can execute a
non-Python command template for each trial.

## Config Shape

```json
{
  "max_evals": 20,
  "seed": 123,
  "command_template": "target.exe --config {config} --out {out}",
  "base_config": {"steps": 1000},
  "search_params": {
    "K": [0.0, 2.0]
  },
  "score_metric_path": "summary.json:final_metrics.order_parameter"
}
```

If `command_template` is omitted, the runner performs a smoke test over generated configs only.

## Usage

```powershell
.\parameter_optimizer_v1_cpp\build_and_run.bat
```
