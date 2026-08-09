# MPF-SIM-005: Recursive Admissibility Phase Transition Mapping

## 1. Purpose
This document performs the **formal documentation** for the phase transition mapping (`MPF-SIM-005`). The goal is to identify and map the transition thresholds where recursive admissibility behavior shifts between different stability regimes (stable, compressed, drifting, metastable, oscillatory, severed, or blocked). This identifies the boundaries of restricted-local proof eligibility.

## 2. Simulation Targets

### 2.1 Admissibility Regime Transition (SIM005-T001)
- **Metric**: `regime_transition_threshold`.
- **Goal**: Identify the exact perturbation levels where a basin shifts from one stability class to another.

### 2.2 Stable-to-Metastable Boundary (SIM005-T002)
- **Metric**: `stable_metastable_margin`.
- **Goal**: Measure the "safety margin" of stable basins before threshold-sensitive behavior emerges.

### 2.3 Metastable-to-Oscillatory Boundary (SIM005-T003)
- **Metric**: `oscillation_onset_threshold`.
- **Goal**: Detect the transition from bounded fluctuations to periodic cycles.

### 2.4 Topology Severance Threshold (SIM005-T004)
- **Metric**: `severance_threshold`.
- **Goal**: Determine when boundary degradation results in structural disconnection of the continuation graph.

### 2.5 Proof Eligibility Phase Boundary (SIM005-T005)
- **Metric**: `proof_eligibility_phase`.
- **Goal**: Map the transition points where basins lose formal proof-eligibility status.

## 3. Simulation Scenarios

- **Stable Basin Perturbation Sweep (SIM005-S001)**: Gradual escalation of noise to find the breakdown of absolute local stability.
- **Lambda Drift Phase Sweep (SIM005-S002)**: Mapping the drift of $\Lambda$ points across varying recursion depths.
- **Boundary Pressure Escalation (SIM005-S003)**: Finding the critical pressure level where scope bleed or boundary inflation occurs.
- **Recursive Composition Phase Sweep (SIM005-S004)**: Mapping the transition from valid local composition to global leakage risks.
- **Failure Geometry Activation Sweep (SIM005-S005)**: Determining the activation thresholds for all registered failure modes.

## 4. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.
- **Allowed Claim**: Simulation results support or challenge restricted-local proof scaffolding only.

---
[Back to Master Index](codex_master_index.md)
