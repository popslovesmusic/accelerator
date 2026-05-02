# Multi-Dimensional TDA Module (v2.0)

This module provides high-performance topological analysis (Persistent Homology) for the "One Process" research ecosystem. It is designed to prove the structural isomorphism of emergent Phase Packets across independent mechanism classes.

## Key Features
- **Higher-Order Homology:**
    - Calculates Betti-0 ($H_0$) for connected component count.
    - Calculates Betti-1 ($H_1$) for loop/cycle detection in both 2D spatial grids and topological networks.
- **Persistence Landscapes:**
    - Performs threshold sweeps to generate barcodes, proving structural persistence across scale.
- **Scientific Rigor:**
    - Emits v2.3 recoverable JSON reports.
    - Includes built-in controls for exact topological shapes.

## Usage

### 1. Build
Requires Intel oneAPI for SYCL/GPU acceleration (can also run on CPU).
```powershell
.\tools\tda_module_v2_cpp\build_and_run.bat
```

### 2. Single Threshold Analysis (Spatial)
```powershell
.\tools\tda_module_v2_cpp\tda_multi_benchmark.exe --mode spatial --file grid.csv --threshold 0.5 --out outputs/tda
```

### 3. Persistence Sweep (Network)
```powershell
.\tools\tda_module_v2_cpp\tda_multi_benchmark.exe --mode network --file adj_matrix.csv --thresh-min 0.1 --thresh-max 0.9 --thresh-steps 10 --out outputs/tda_sweep
```

## Governance
This tool is certified at **Level C5**. All metrics (Betti numbers, persistence vectors) map directly to theoretical structural identity claims.
