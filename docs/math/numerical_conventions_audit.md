# Numerical Conventions Audit (AUDIT-001)

This document tracks numerical conventions, assumptions, and identified risks in the current implementation of the Mono-Process Framework engines as of May 13, 2026.

## Reaction-Diffusion (RD) Moving Boundary Engine

### Boundary Conditions
- **Observation:** The `laplacian` and `channeled_divergence` implementations in `tools/rd_moving_boundary_sim_v1/rd_engine.py` use `np.roll`.
- **Convention:** This implies **periodic boundary conditions** in both X and Y axes.
- **Risk:** Periodic boundaries may not be appropriate for all "moving boundary" simulations, especially if the domain approaches the edge of the grid.
- **Status:** Staged for review. Deferred behavioral change until a global boundary policy is approved.

### Discretization and Scaling
- **Observation:** The Laplacian and divergence terms do not include explicit `dx` or `dy` scaling.
- **Convention:** This assumes a **unit-grid spacing** ($dx = dy = 1$).
- **Risk:** Physical interpretations requiring specific spatial scales must currently adjust coefficients (e.g., $D_{diff}$) to compensate.
- **Status:** Staged for review. Unit-grid convention is documented; explicit scaling patch may follow.

## Topological Data Analysis (TDA) Module

### Adjacency Graph Connectivity
- **Observation:** Adjacency in `tools/tda_module_v1/tda_engine.py` may be sensitive to floating-point noise in the signal field.
- **Risk:** Over-connectivity or spurious persistent homology components.
- **Status:** Staged for review. A thresholding patch with an explicit default policy is recommended.

## Accelerator Simulation (C++)

### Poisson Solver Sign Convention
- **Observation:** The Poisson solver in `tools/accelerator_sim_v1_cpp/PoissonSolver.cpp` requires a sign convention audit.
- **Risk:** Potential mismatch with electromagnetic force conventions in downstream dynamics.
- **Status:** Staged for review. Downstream usage must be audited before any sign change.

## Reproducibility and Dependencies

### Unpinned Requirements
- **Observation:** `requirements.txt` currently contains unpinned dependencies.
- **Risk:** Floating versions of `numpy`, `scipy`, or `pandas` may introduce subtle numerical drift between environments.
- **Status:** Staged for follow-up (PATCH-AUDIT002).

## High-Confidence Fixes (Applied)

### RD Short-Run Crash
- **Bug:** `tools/rd_moving_boundary_sim_v1/sim.py` crashed on runs shorter than 10 steps due to empty `history` list indexing.
- **Fix:** Added guard for empty history and fallback to current engine metrics.
- **Verification:** Regression test `tests/test_rd_moving_boundary_short_runs.py` passes.
