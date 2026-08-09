# RD Boundary and Scaling Policy (AUDIT-004)

This document defines the numerical and discretization conventions for the Reaction-Diffusion (RD) moving-boundary simulation engine.

## 1. Boundary Conditions
- **Default Mode:** `periodic`
- **Implementation:** Uses `np.roll` to shift fields, which wraps values around the grid edges.
- **Explicitness:** The `boundary_mode` parameter in the simulation configuration must default to `periodic`.
- **Future Expansion:** Reflecting (Neumann) and Dirichlet boundary modes are staged for future implementation but are NOT currently enabled. Any change to non-periodic behavior requires a new controlled patch.

## 2. Grid Scaling (Discretization)
- **Default Scaling:** Unit-grid spacing ($dx = 1.0, dy = 1.0$).
- **Implementation:** Laplacian and divergence operators currently omit explicit $dx$ and $dy$ terms in the denominator, effectively assuming unit spacing.
- **Explicitness:** The `dx` and `dy` parameters are now available in the configuration and default to `1.0`.
- **Future Expansion:** Support for non-unit $dx$ and $dy$ scaling (e.g., for physical units or convergence studies) is staged. A future patch will be required to update the numerical operators to correctly handle non-unit scaling without breaking legacy model results.

## 3. Legacy Preservation
- All existing simulation results and theoretical mappings assume `periodic` boundaries and `unit-grid` scaling.
- The `RDEngine` must preserve these behaviors by default to ensure reproducibility of established findings (AUDIT-002).

## 4. Governance Constraints
- **Claim Humility:** Simulation results near the grid boundary must acknowledge the periodic wrapping effect unless the domain is sufficiently localized.
- **Verification:** Claims of "infinite domain" behavior or "scale invariance" are prohibited without explicit $dx/dy$ convergence evidence.
- **Promotion:** `implementation_verified` claims for the RD engine are restricted to the unit-grid, periodic-boundary regime until further validation is completed.
