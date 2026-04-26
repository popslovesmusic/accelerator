# `summarize_runs.py`

Scans `**/summary.json` under a root directory and emits a tidy CSV of flattened config + final metrics.

If `matplotlib` is installed, it can also generate quick histogram plots and an optional sweep plot.

## Examples

Summarize all runs under `outputs/`:

```powershell
python utilities/summarize_runs.py --root outputs
```

Summarize a specific program run directory:

```powershell
python utilities/summarize_runs.py --root outputs/research_residue_necessity_2026-04-25/runs
```

Add plots (if Matplotlib is available):

```powershell
python utilities/summarize_runs.py --root outputs --plots
```

Make a sweep plot:

```powershell
python utilities/summarize_runs.py `
  --root outputs/research_residue_necessity_2026-04-25/runs `
  --plots `
  --sweep-x config.residue_growth `
  --sweep-y final.active_fraction `
  --sweep-group run_name
```

## Output

By default:

- CSV: `<root>/analysis_summaries/runs_summary.csv`
- Plots: `<root>/analysis_summaries/plots/`

