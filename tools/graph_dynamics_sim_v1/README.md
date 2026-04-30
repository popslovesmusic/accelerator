# Dynamic Graph / Network Dynamics Simulation (v1)

This simulation models a network of nodes with internal phase states where the topology itself (edges) is dynamic, governed by local state alignment and stress-based admissibility rules.

## Theoretical Basis

- **Topological CSI:** Causal influence is restricted to the network's adjacency structure.
- **Decoupling:** Edges are removed if the stress (state difference) between nodes exceeds a threshold.
- **Recoupling:** New edges form between disconnected nodes if their states align.
- **Causal Accessibility:** The set of nodes a node can reach depends on the current active topological corridors.

## Model Equations

### Node Phase Update
$d\phi_i/dt = \omega_i + \frac{K}{N} \sum_{j} A_{ij} \sin(\phi_j - \phi_i)$

### Rewiring Rules
- **Decouple:** Remove edge $(i, j)$ if $|\sin(\phi_i - \phi_j)| > \theta_{\text{decouple}}$
- **Recouple:** Add edge $(i, j)$ with probability $P$ if $|\sin(\phi_i - \phi_j)| < \theta_{\text{recouple}}$

## Usage

```powershell
python sim.py --config configs/default.json --out outputs/graph_run_01
```

## Outputs

- `metrics.csv`: Time-series of graph connectivity metrics (avg degree, connected components).
- `summary.json`: Final state and configuration.
- `plots/`: Visualizations of the network graph (if NetworkX and Matplotlib are installed).
