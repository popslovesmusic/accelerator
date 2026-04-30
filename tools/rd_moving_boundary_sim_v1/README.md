# Reaction-Diffusion Moving Boundary Simulation (v1)

This simulation models a coupled system where an "admissibility domain" ($D$) and a "signal process" ($S$) co-evolve. The domain itself deforms and moves based on the signal intensity, carves corridors through inert space, and forms isolated pockets.

## Theoretical Basis

- **Moving Boundaries:** The spatial domain of admissibility is dynamic, not fixed.
- **Corridor Formation:** Channels of admissibility created by the propagation of an active signal.
- **Dynamic Topology:** The ability of the domain to fracture, merge, and reform based on internal state pressure.
- **Basins & Pockets:** Stable regions of high signal density that sustain a local domain even when disconnected from the primary source.

## Model Equations

### Domain Evolution (Phase-Field)
$$\frac{\partial D}{\partial t} = D_{diff} \nabla^2 D + \beta D(1-D)(S - \theta_{growth}) - \gamma D$$

### Signal Diffusion (Channeled)
$$\frac{\partial S}{\partial t} = \nabla \cdot (D_{S} D \nabla S) + \text{Source} - \alpha S$$

The term $\nabla \cdot (D \nabla S)$ ensures the signal only diffuses within the active domain $D$.

## Usage

```powershell
python sim.py --config configs/default.json --out outputs/rd_run_01
```

## Outputs

- `metrics.csv`: Time-series of active domain area and total signal mass.
- `summary.json`: Final state and configuration summary.
- `plots/`: Heatmaps showing the co-evolution of the Domain and Signal.
