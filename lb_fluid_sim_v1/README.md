# Lattice Boltzmann Fluid-like Simulation (v1)

This simulation implements a 2D Lattice Boltzmann Method (LBM) using the D2Q9 model. It includes dynamic topology through "erosion," where fluid stress can break down solid boundaries, simulating the interaction between the **Load Channel** (fluid) and the **Closure Channel** (constraints).

## Theoretical Basis

- **LBM D2Q9:** A mesoscopic fluid model based on particle distribution functions.
- **Load Channel ($\Sigma$):** Represented by the active fluid momentum and flow.
- **Closure Channel ($\rho$):** Represented by the solid boundary constraints.
- **Dynamic Erosion:** Boundaries are not static; they fail and become part of the flow domain when local stress exceeds a threshold, modeling the evolution of causal corridors.

## Model Equations

### LBM Step
1. **Collision:** $f_i(x, t+\Delta t) = f_i(x, t) - \frac{1}{\tau} (f_i - f_i^{eq})$
2. **Streaming:** $f_i(x+e_i\Delta t, t+\Delta t) = f_i(x, t+\Delta t)$

### Erosion Rule
A boundary cell $(x,y)$ becomes fluid if:
$$|\mathbf{u}_{neighbor}| \cdot \rho_{neighbor} > \text{Threshold}$$

## Usage

```powershell
python sim.py --config configs/default.json --out outputs/lb_run_01
```

## Outputs

- `metrics.csv`: Time-series of fluid volume and mean velocity.
- `summary.json`: Final parameters and status.
- `plots/`: Velocity magnitude heatmaps and boundary evolution (if Matplotlib is installed).
