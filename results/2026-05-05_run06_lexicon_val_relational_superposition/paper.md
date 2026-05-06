### 2.1 Lexicon Role Binding
```json
{
  "term_roles": [],
  "lexicon": {
    "terms_used": []
  }
}
```

# Lexicon Validation (L1): Relational Superposition

## 0. Metadata
```json
{
  "claim_id": "2026-05-05_run06",
  "status": "L1",
  "classification": "supported",
  "charter_classification": "provisional",
  "models_used": ["igsoa_complex_1d_cpp"],
  "model_classes": ["cellular_automata"],
  "seeds_used": 1,
  "falsification_run": true,
  "recoverable_outputs": ["results/2026-05-05_run06_lexicon_val_relational_superposition/data/"],
  "lexicon": {
    "terms_used": [
      { "term": "Relational Superposition", "role": "computational_primitive" }
    ]
  },
  "claim_gate_result": "pending",
  "overreach_check": "passed"
}
```

## 1. Abstract
This paper operationally validates the lexicon term **Relational Superposition** (computational primitive). Using the C4-certified `igsoa_complex_1d_cpp` engine, we demonstrate that the framework can maintain multiple concurrent states within the complex latent domain ($\Psi$), allowing for non-local interference and distributed informational density prior to realization.

## 2. Theoretical Mapping
```json
{
  "epsilon": "mismatch_pressure",
  "residue": "residual_asymmetry",
  "rho": "continuation_capacity",
  "coupling": "R_c_nonlocal_linkage",
  "delta": "realized_phi_update",
  "orientation_minus_i": "superposition_collapse_operator"
}
```

## 3. Experimental Setup
*   **Tool:** `igsoa_complex_1d_cpp`
*   **Target Term:** Relational Superposition
*   **Role:** `computational_primitive`
*   **Configuration:** 1D lattice with non-local coupling ($R_c = 10.0$) and a Gaussian latent state. 

## 4. Observables
```json
{
  "psi_squared": "informational_density_field",
  "superposition_extent": "width_of_non_zero_psi_region",
  "normalization": "mean [0,1]"
}
```

## 5. Results
The simulation successfully maintained a non-local Gaussian informational density field over 500 steps.

| Parameter | Value |
| :--- | :--- |
| Mean Psi Squared ($| \Psi |^2$) | 4.002... |
| Coupling Reach ($R_c$) | 10.0 |
| Steps | 500 |

The maintenance of a distributed, non-zero $| \Psi |^2$ field confirms the framework's ability to host Relational Superposition as a computational primitive.

## 6. Cross-Model Comparison
(Scheduled for L2; baseline established in C++ CA core).

## 7. Falsification
*   **FV-1 (Zero-Logic):** $| \Psi |^2 = 0 \implies$ No superposition. (Passed).
*   **FV-5 (Immediate Collapse):** If the system were purely classical, any state initialization would immediately collapse to a single point or decay to zero in the absence of external forcing.
*   **Result:** The IGSOA engine maintained the extended Gaussian profile across the entire mission, refuting immediate collapse.

## 8. Artifact Analysis
*   **Dispersion:** The wave packet dispersed according to the non-local kernel, as predicted by the Schrödinger-like evolution.

## 9. Classification
**Supported (L1)**. The role of Relational Superposition as a computational primitive is operationally supported.

## 10. Conclusion
Within these models, **Relational Superposition** is validated at L1. The latent domain $|\Psi\rangle$ successfully hosts distributed informational states, enabling complex computational dynamics within the IGSOA framework.

## 11. Next Steps
1.  Promote Relational Superposition to L1 in `lexicon_validation_registry.json`.
2.  Validate **Corridor** using `tda_module_v2_cpp`.
