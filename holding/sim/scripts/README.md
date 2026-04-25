# Paper 1 Figure Scripts

This kit contains three standalone plotting scripts for Paper 1.

## Included scripts

1. `plot_figure1_timeseries.py`
   - Plots representative epsilon/rho/R trajectories from a `timeseries_global.csv` file.
   - Intended figure: representative persistence / near-floor time series.

2. `plot_figure2_regime_map.py`
   - Builds a simple regime map from a CSV with parameter columns and `regime_classification`.
   - Intended figure: parameter-to-regime map.

3. `plot_figure3_floor_convergence.py`
   - Plots epsilon floor estimates against dt and/or t_final from refinement outputs.
   - Intended figure: near-floor convergence / refinement behavior.

4. `run_paper2_relational_geodesic_prototype.py`
   - Builds a minimal Paper 2 weighted-graph prototype with three designed regimes:
     corridor, shelf-transition, and decoupling.
   - Writes governed outputs under `artifacts/runs/` and saves a manuscript figure to
     `docs/manuscript/paper2/fig1_relational_geodesic_regimes.png`.

5. `run_paper3_i_field_probe.py`
   - Computes an explicit local `(L,Q)` argmin field (a proxy for `O*`) and the induced `-(i)` direction field.
   - Writes governed outputs under `artifacts/runs/` and saves a manuscript figure to
     `docs/manuscript/paper3/fig2_i_field_quiver.png`.

## Assumptions

These scripts try to be tolerant about column names, but they assume CSVs roughly matching your governed outputs.
If your exact column names differ, edit the `COLUMN CANDIDATES` section near the top of each script.

## Usage examples

python plot_figure1_timeseries.py --input timeseries_global.csv --output figure1_timeseries.png
python plot_figure2_regime_map.py --input classification_summary.csv --x k --y beta --output figure2_regime_map.png
python plot_figure3_floor_convergence.py --input top_refined_floor_candidates.csv --output figure3_floor_convergence.png
python run_paper2_relational_geodesic_prototype.py
python run_paper3_i_field_probe.py

## Notes

- These scripts use matplotlib only.
- They do not set custom colors or styles.
- They save PNG figures to the path you provide.
