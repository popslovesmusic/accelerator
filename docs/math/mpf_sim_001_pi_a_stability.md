# MPF-SIM-001: Restricted Local Pi_A Stability Simulation Harness

## 1. Purpose
This document performs the **formal documentation** for the simulation harness (`MPF-SIM-001`). The goal of this harness is to empirically test the recursive application of the $\Pi_A$ projection operator across different classes of local admissibility basins. It serves to validate or challenge the restricted-local proof scaffolding developed in the `MPF-PF` series.

## 2. Simulation Targets

### 2.1 Pi_A Recursive Projection
- **Goal**: Check whether verified stable basins (`RSB-STABLE`) maintain idempotent persistence under repeated projection.
- **Metric**: Idempotence error $| \Pi_A^n(x) - \Pi_A^{n-1}(x) |$.

### 2.2 Boundary Hardening Stress
- **Goal**: Test for hidden boundary inflation or scope bleed by applying perturbation to metastable basins.
- **Metric**: Activation of threshold-sensitive metastability (`FG-A006`).

### 2.3 Failure Geometry Activation
- **Goal**: Verify that preserved blockers (e.g., topology severance, identity ambiguity) trigger correctly in ineligible basins.
- **Metric**: Explicit logging of `failure_geometry_triggered`.

## 3. Simulation Outcomes (Summary)
The simulation runner iterates through four primary basin scenarios:
- **RSB-STABLE**: Expected to show minimal error and high proof eligibility.
- **RSB-METASTABLE**: Expected to show stability in standard runs but fail under perturbation.
- **RSB-SEVERED**: Expected to show immediate collapse and topology severance trigger.
- **RSB-AMBIGUOUS**: Expected to show image persistence but trigger identity ambiguity.

## 4. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.
- **Allowed Claim**: Simulation results support or challenge restricted-local proof scaffolding only.

---
[Back to Master Index](codex_master_index.md)
