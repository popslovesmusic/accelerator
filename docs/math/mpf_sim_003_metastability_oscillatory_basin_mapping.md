# MPF-SIM-003: Metastability and Oscillatory Basin Mapping

## 1. Purpose
This document performs the **formal documentation** for the simulation mapping (`MPF-SIM-003`). The purpose is to map metastable and oscillatory basin behavior under recursive $\Pi_A$ application. It differentiates between bounded local fluctuations and proof-blocking instabilities, ensuring that true restricted-local stability is separated from fragile or cyclic basin behavior.

## 2. Simulation Targets

### 2.1 Metastability Detection (SIM003-T001)
- **Metric**: `metastability_score`.
- **Goal**: Measure whether local idempotence remains bounded but highly sensitive to admissibility thresholds.

### 2.2 Oscillatory Loop Detection (SIM003-T002)
- **Metric**: `projection_cycle_period`.
- **Goal**: Detect cases where repeated application of $\Pi_A$ results in a stable cycle between multiple images rather than a single fixed point.

### 2.3 Idempotence Error Envelope (SIM003-T003)
- **Metric**: `idempotence_error_envelope`.
- **Goal**: Track the min, max, mean, and drift of the idempotence error $| \Pi_A(x) - x |$ over recursive iterations.

### 2.4 Threshold Crossing Sensitivity (SIM003-T004)
- **Metric**: `threshold_crossing_count`.
- **Goal**: Identify how many times a projection sequence transitions between different stability classifications under minor perturbations.

### 2.5 Proof Eligibility Impact (SIM003-T005)
- **Metric**: `proof_eligibility_impact`.
- **Goal**: Formally classify whether the observed behavior remains eligible for local proof scaffolding or if it must be blocked/flagged for review.

## 3. Simulation Scenarios

- **Bounded Metastable Basin (SIM003-S001)**: Fluctuation remains within a bounded envelope; requires manual review.
- **Oscillatory Projection Cycle (SIM003-S002)**: Sequence settles into a periodic cycle; classified as `RSB-OSCILLATORY`.
- **Threshold-Sensitive Transition (SIM003-S003)**: Infinitesimal perturbation triggers a transition to an ineligible state or activation of failure geometry.
- **False Stability Trap (SIM003-S004)**: Sequence appears stable for $N$ iterations but diverges or cycles for $M > N$.
- **Stable Control Basin (SIM003-S005)**: Baseline stable basin with near-zero error and no triggers.

## 4. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.
- **Allowed Claim**: Simulation results support or challenge restricted-local proof scaffolding only.

---
[Back to Master Index](codex_master_index.md)
