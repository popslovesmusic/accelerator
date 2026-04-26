# Cellular Automata Admissibility Simulation (v1)

This simulation implements a 2D Continuous Threshold Cellular Automata designed to test the concepts of **Admissibility** and **Zero Logic** as defined in "THE LAW OF THE ONE PROCESS."

## Theoretical Basis

- **Zero is not Absence:** A cell with a value of 0 is not "empty" but represents perfect symmetry.
- **Admissibility:** A cell only updates its state if the gradient (difference) from its neighbors exceeds its internal **Residue** threshold.
- **Residue ($R$):** An internal threshold that grows when a cell is active (admissible) and decays when it is inert (decoupled).

## Model Equations

### Admissibility Condition
An update to cell $(i,j)$ is admissible at time $t$ if:
$$\Delta_{i,j}(t) > R_{i,j}(t)$$
where $\Delta_{i,j}$ is the local mismatch gradient (sum of differences with neighbors).

### Update Law
If admissible:
$$\epsilon_{i,j}(t+1) = \epsilon_{i,j}(t) + D \cdot \text{Laplacian}(\epsilon)_{i,j}$$
If not admissible:
$$\epsilon_{i,j}(t+1) = \epsilon_{i,j}(t)$$

### Residue Evolution
$$R_{i,j}(t+1) = R_{i,j}(t) \cdot (1 - \gamma_R) + \delta_R \cdot \text{ActiveMask}_{i,j}$$

## Usage

```powershell
python sim.py --config configs/default.json --out outputs/ca_run_01
```

## Reproducible stochastic initialization (optional)

The CA update rule is deterministic, but you can introduce *seeded* run-to-run variability by adding Gaussian noise at initialization:

- `epsilon_noise_std` (default `0.0`): stddev of noise added to the initial mismatch field `epsilon`.
- `residue_noise_std` (default `0.0`): stddev of noise added to the initial residue field `R` (clamped to nonnegative after noise).
- `seed`: RNG seed used for the initialization noise.

This preserves existing behavior unless you set the noise stddevs to non-zero values.

## Outputs

- `metrics.csv`: Time-series of active cell fraction and mean mismatch.
- `summary.json`: Final parameters and status.
- `snapshots/`: Heatmaps of the $\epsilon$ and $R$ fields (if Matplotlib is installed).
