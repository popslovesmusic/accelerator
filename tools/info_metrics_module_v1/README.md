# Information / Entropy Tracking Engine (v1)

This module provides model-independent measures of structure vs. noise for all simulators in the `acellorator` ecosystem. It acts as a standalone post-processor that computes information-theoretic metrics from simulation snapshots.

## Theoretical Basis

- **Shannon Entropy (H):** Quantifies the uncertainty or disorder in the state distribution. Low entropy indicates highly ordered, clustered, or uniform states.
- **Mutual Information (MI):** Measures the statistical dependence between different parts of the system or across different timesteps. High MI indicates strong structural coupling.
- **Compression Complexity:** A proxy for Kolmogorov complexity. It uses the `zlib` compression ratio to measure how "compressible" (and thus structured) the state data is.

## Metrics Defined

1. **Entropy:** $H(X) = - \sum P(x) \log P(x)$ (computed via histogram binning).
2. **Complexity:** $\mathcal{C} = \frac{\text{Compressed Size}}{\text{Uncompressed Size}}$.
3. **Mutual Information:** $MI(X, Y) = H(X) + H(Y) - H(X, Y)$.

## Usage

Analyze a specific simulation output directory:

```powershell
python analyze_info.py --dir ../circular_accelerator_sim_v1/outputs/ring_default
```

## Outputs

- `info_evolution.csv`: Time-series of Entropy, Complexity, and MI.
- `info_summary.json`: Aggregate stats and structure-formation timestamps.
- `plots/`: Visualizations of informational metrics over time.
