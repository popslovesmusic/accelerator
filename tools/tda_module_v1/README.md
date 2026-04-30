# Topological Data Analysis (TDA) Module (v1)

This module provides quantitative definitions for structural changes in simulation fields and networks, moving beyond visual heuristics to formal topological metrics.

## Theoretical Basis

- **Connected Components ($H_0$):** Measures the degree of fragmentation or coupling in a domain.
- **Pockets vs. Corridors:** A single massive component represents a coupled "corridor," while many small components represent isolated "pockets."
- **Percolation:** The point where a single component spans the entire domain, representing a global structural transition.

## Usage

Analyze a directory of 2D snapshots:

```powershell
python analyze_topology.py --dir ../rd_moving_boundary_sim_v1/outputs/run_01 --threshold 0.5
```

## Metrics Defined

1. **Component Count:** Total number of isolated domains.
2. **Max Component Size:** Area of the largest connected structure (normalized by total active area).
3. **Mean Component Size:** Average size of isolated pockets.
4. **Active Area Fraction:** Total fraction of the grid that is above the threshold.

## Outputs

- `topology_evolution.csv`: Time-series of topological metrics.
- `topology_summary.json`: Final state and fragmentation analysis.
- `plots/`: Visualizations of component count and size distributions.
