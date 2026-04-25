# Kuramoto Oscillator Network Simulation (v1)

This simulation models a 1D ring of coupled non-linear oscillators to study phase-locking, synchronization, and the emergence of "shelf regimes."

## Theoretical Basis

- **Kuramoto Dynamics:** Oscillators influence each other's phases based on the sine of their phase difference.
- **Local Coupling (Ring Topology):** Each oscillator only interacts with its immediate left and right neighbors.
- **Shelf Regimes:** Metastable spatial domains of partial synchronization.
- **$-(i)$ / Mismatch:** The phase difference at the boundaries of synchronized domains.

## Model Equations

### Governing Equation
$$d\phi_i/dt = \omega_i + K \sum_{j \in \text{Neighbors}} \sin(\phi_j - \phi_i)$$

For a 1D ring:
$$d\phi_i/dt = \omega_i + K [\sin(\phi_{i+1} - \phi_i) + \sin(\phi_{i-1} - \phi_i)]$$

## Usage

```powershell
python sim.py --config configs/default.json --out outputs/kuramoto_run_01
```

## Outputs

- `metrics.csv`: Time-series of global order parameter and local coherence.
- `summary.json`: Final state and configuration summary.
- `plots/`: Spatiotemporal phase heatmaps and order parameter evolution.
