# Structural Box Simulation (v2)

This is a "Level 2" research simulator promoted from the `holding` directory. It implements the refined **Structural Preservation Model (SPM)**, focusing on the co-evolution of Mismatch ($\epsilon$), Constraint ($\rho$), and Residue ($R$).

## Theoretical Basis

- **Identity Persistence:** Tracking whether a localized structural domain (the "Box") can maintain its integrity over long temporal horizons.
- **SRC (Structural Relational Closure):** Testing for the emergence of self-maintaining relational structures within the phase-space.
- **Three-Channel Decomposition:**
    - **$\epsilon$ (Mismatch):** The active signal or deviation.
    - **$\rho$ (Constraint):** The closure/boundary enforcement.
    - **$R$ (Residue):** The accumulated historical inscription.

## Promotion Notes

This tool replaces the simpler conceptual models (v1) with a rigorous 1D PDE implementation used in Phase 3/4 research (`sim11` through `sim17`). It supports complex initial conditions (gaussian bumps, uniform fields) and specialized "Box" screening metrics.

## Usage

```powershell
python sim.py --config configs/default.json --out outputs/l2_run_01
```

## Outputs

- `timeseries_global.csv`: Global averages of $\epsilon, \rho, R$.
- `final_summary.json`: Detailed SRC/Box screening results.
- `metrics.csv`: Standard compatibility metrics for the ensemble orchestrator.
