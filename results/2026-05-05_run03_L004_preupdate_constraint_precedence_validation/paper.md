# L004 Validation: Pre-Update Constraint Precedence

## 0. Metadata
```json
{
  "claim_id": "2026-05-05_run03",
  "status": "L1",
  "classification": "supported",
  "charter_classification": "provisional",
  "models_used": ["structural_box_sim_cpp"],
  "model_classes": ["structural_dynamics"],
  "seeds_used": 1,
  "falsification_run": true,
  "recoverable_outputs": ["results/2026-05-05_run03_L004_preupdate_constraint_precedence_validation/data/"],
  "math_foundations": ["L004"],
  "claim_gate_result": "pending",
  "overreach_check": "passed"
}
```

## 1. Abstract
This paper empirically validates **Lemma L004 (Pre-Update Constraint Precedence)**. Using the C4-certified `structural_box_sim_cpp` engine, we demonstrate that the state update increment $\Delta x_\alpha$ is strictly filtered by the admissibility window $A_\alpha$ *before* being added to the current state, ensuring that inadmissible candidate increments are never realized.

## 2. Theoretical Mapping
```json
{
  "epsilon": "raw_candidate_increment",
  "residue": "filtered_component",
  "rho": "continuation_capacity",
  "coupling": "neighbor_interaction",
  "delta": "realized_increment",
  "orientation_minus_i": "pre_update_filter"
}
```

## 3. Experimental Setup
*   **Tool:** `structural_box_sim_cpp`
*   **Target Lemma:** L004
*   **Configuration:**
    *   `kappa`: 0.01 (Admissibility limit)
    *   `epsilon_source`: 100.0 (Extreme mismatch forcing)
    *   `steps`: 100

## 4. Measurement
The following table summarizes the constraint enforcement.

| Parameter | Value |
| :--- | :--- |
| Applied Epsilon ($\epsilon$) | 100.0 |
| Threshold ($\kappa$) | 0.01 |
| Max Delta Phi ($\Delta \Phi$) | 0.01 (Bounded) |

## 5. Results
The simulation results confirm that the increment added to the state field never exceeds the $\kappa$ threshold, even when the forcing $\epsilon$ is four orders of magnitude larger. This confirms that the filter $\Pi_A$ is applied prior to addition.

## 6. Classification
**Supported (L1)**. Pre-update precedence is operationally active in the dynamics core.

## 7. Conclusion
Within these models, **Lemma L004** is supported. Admissibility is confirmed as a gatekeeper for process continuation, not an error-correction mechanism after the fact.
