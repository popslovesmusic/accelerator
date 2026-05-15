# MPF-SIM-011: Recursive Admissibility Hysteresis Mapping

## 1. Purpose
This document performs the **formal documentation** for the simulation mapping (`MPF-SIM-011`). The goal is to map whether admissibility response depends on recursive history, specifically testing whether recovery, decay, and reset paths differ from the original path of instability. This identifies path-dependent residues that influence local stability regimes.

## 2. Simulation Targets

### 2.1 Admissibility Hysteresis Loop (SIM011-T001)
- **Metric**: `hysteresis_loop_area`.
- **Goal**: Measure the integral difference between the path of admissibility loss (destabilization) and the path of admissibility gain (recovery).

### 2.2 Recovery Path Asymmetry (SIM011-T002)
- **Metric**: `recovery_asymmetry_index`.
- **Goal**: Quantify whether the re-entry into a stable state occurs through a different structural configuration than the initial departure.

### 2.3 Scar Irreversibility (SIM011-T003)
- **Metric**: `scar_irreversibility_score`.
- **Goal**: Determine if prior activation of failure geometry (e.g., topology severance) leaves non-reversible deformations in the constraint structure.

### 2.4 Reset Completeness (SIM011-T004)
- **Metric**: `reset_completeness_score`.
- **Goal**: Verify whether a system reset truly removes prior bias (groove influence) or if history continues to leak into future iterations.

### 2.5 Proof Eligibility Hysteresis (SIM011-T005)
- **Metric**: `proof_eligibility_hysteresis`.
- **Goal**: Identify if proof eligibility follows a different threshold logic on the recovery path than on the loss path.

## 3. Simulation Scenarios

- **Stable-to-Metastable-to-Stable Loop (SIM011-S001)**: Recovery path differs but remains review-safe.
- **Severance Scar Irreversibility (SIM011-S002)**: Topology severance leaves persistent scar even after recovery.
- **False Reset Hysteresis (SIM011-S003)**: Residual groove bias reactivates instability after apparent reset.
- **Compressed Recovery Path (SIM011-S004)**: Recovered basin has narrower margins than original.
- **Control Reversible Basin (SIM011-S005)**: Paths overlap with low hysteresis.

## 4. Hysteresis Classes

- **SIM-HYSTERESIS-REVERSIBLE**: Recovery retraces loss path. Supports formal review.
- **SIM-HYSTERESIS-ELASTIC**: Recovery path differs but remains admissible. Review required.
- **SIM-HYSTERESIS-PLASTIC**: System retains lasting deformation. Review required or blocked.
- **SIM-HYSTERESIS-SCARRED**: Irreversible or recurring instability. Blocked.
- **SIM-HYSTERESIS-DECEPTIVE**: Hidden instability from residual bias. Blocked.

## 5. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.
- **Allowed Claim**: Hysteresis behavior support formal review only; it does not constitute mathematical proof or global closure.

---
[Back to Master Index](codex_master_index.md)
