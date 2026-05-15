# MPF-SIM-002: Recursive Boundary Inflation Stress Test

## 1. Purpose
This document performs the **formal documentation** for the simulation stress test (`MPF-SIM-002`). The purpose is to empirically determine whether restricted-local admissibility composition remains bounded under recursive $\Pi_A$ application, or if it leaks into hidden boundary expansion / implicit globalization. This test addresses the most dangerous unresolved pathway: local composition behavior mimicking global closure.

## 2. Simulation Targets

### 2.1 Boundary Inflation Detection (SIM002-T001)
- **Metric**: `boundary_growth_ratio`.
- **Goal**: Detect expansion of the admissibility domain beyond the declared $D_L$.

### 2.2 Scope Bleed Detection (SIM002-T002)
- **Metric**: `scope_bleed_flag`.
- **Goal**: Identify recursive leakage from the local proof region into undeclared domains.

### 2.3 Composition Leakage Detection (SIM002-T003)
- **Metric**: `composition_leakage_score`.
- **Goal**: Measure whether recursive application of LAW034 local composition rules results in emergent global-like behavior.

### 2.4 Idempotence Drift (SIM002-T004)
- **Metric**: `idempotence_error_delta`.
- **Goal**: Track if repeated projection error increases as boundary pressure accumulates.

### 2.5 Failure Geometry Activation (SIM002-T005)
- **Metric**: `failure_geometry_triggered`.
- **Goal**: Record which preserved blockers (e.g., topology severance) trigger under recursive stress.

## 3. Simulation Scenarios

- **Stable Local Boundary (SIM002-S001)**: Baseline stability where boundaries remain fixed.
- **Metastable Boundary (SIM002-S002)**: Bounded oscillatory behavior requiring review.
- **Hidden Boundary Inflation (SIM002-S003)**: Failure mode where domain constraints are silently violated.
- **Recursive Composition Leakage (SIM002-S004)**: Failure mode where local grammar chains into global closure.
- **Topology Severance Under Stress (SIM002-S005)**: Triggering of severance blockers under boundary pressure.

## 4. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.
- **Allowed Claim**: Simulation results support or challenge restricted-local proof scaffolding only.

---
[Back to Master Index](codex_master_index.md)
