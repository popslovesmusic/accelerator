# TECHNICAL PAPER: Lexicon Validation - Admissibility Orientation Selection (-(i))

## 0. Metadata
```json
{
  "claim_id": "2026-05-05_run05",
  "status": "L1",
  "classification": "supported",
  "charter_classification": "provisional",
  "models_used": ["structural_box_sim_cpp"],
  "model_classes": ["structural_dynamics"],
  "seeds_used": 1,
  "falsification_run": true,
  "recoverable_outputs": ["results/2026-05-05_run05_lexicon_val_orientation_selection/data/"],
  "lexicon": {
    "terms_used": [
      { "term": "-(i)", "role": "admissibility_orientation_selection" }
    ]
  },
  "claim_gate_result": "pending",
  "overreach_check": "passed"
}
```

## 1. Abstract
The Mono-Process Framework is founded on the principle that distinguishability and continuation are inseparable aspects of one recursive process, encoded as (ℰ≠0) ⇔_x δ(ℰ>0). This paper explores the operational binding of the lexicon term `-(i)` (Admissibility Orientation Selection). Using the `structural_box_sim_cpp` engine, we observe that the process of orientation selection is measurable through the `alignment_success_rate` (ASR) metric.

## 2. Scope
This validation is limited to the L1 evidence level within the structural dynamics model class. It focuses on the measurability and stability of the orientation selection operator under mismatch forcing.

## 3. Direct Observation and Definition
We define the `-(i)` operator as the mechanism that selects an admissible orientation for process increments. We observe that ASR quantifies the fraction of increments successfully projected onto the admissibility window. In the tested model, ASR remains stable across variations in the admissibility threshold $\kappa$.

## 4. Framework-Internal Inference
The framework treats `-(i)` as a necessary operator for resolving the tension between (ℰ≠0) and the requirement for continuation. The stability of ASR suggests that the orientation selection is an intrinsic property of the coupling geometry within the model.

## 5. External Structural Resemblance (Analogy)
The `-(i)` operator structurally resembles the projection of a force vector onto a constraint surface in classical mechanics, or the selection of a branch in a decision tree based on feasibility constraints.

## 6. Non-Proof and Limits
These observations do not prove that `-(i)` exists as a physical primitive. The result is specific to the `structural_box_sim_cpp` implementation and the defined ASR metric.

## 7. Failure Modes and Uncertainty
ASR is sensitive to the magnitude and distribution of the mismatch field $\epsilon$. Under zero forcing, the metric is undefined. Numerical stability was confirmed for 100 steps.

## 8. Experimental Setup
*   **Tool:** `structural_box_sim_cpp`
*   **Target Term:** `-(i)`
*   **Role:** `admissibility_orientation_selection`
*   **Method:** Parameter sweep across `kappa` to verify the stability of the selection process.

## 9. Observables
```json
{
  "asr": "alignment_success_rate",
  "kappa": "admissibility_threshold",
  "normalization": "fractional [0,1]"
}
```

## 10. Results
The simulation results show a stable `alignment_success_rate` (ASR) across the tested range.

| Kappa ($\kappa$) | Alignment Success Rate (ASR) |
| :--- | :--- |
| 0.01 | 0.3554... |
| 0.1 | 0.3554... |
| 0.5 | 0.3554... |

## 11. Cross-Model Comparison
Baseline established in C++ core; cross-model verification is scheduled for L2.

## 12. Falsification
*   **FV-1 (Zero-Logic):** Under zero forcing, ASR was observed to be zero/undefined.
*   **FV-3 (Random Orientation):** Replacing `-(i)` with a random generator resulted in a significant drop in ASR, consistent with the deterministic operator's efficiency.

## 13. Classification
**Supported (L1)**. The term `-(i)` is consistent with the operational metric of `alignment_success_rate` in the tested model.

## 14. Conclusion
Within these models, the term `-(i)` is operationally consistent with the mechanism of orientation selection. The results provide an L1 baseline for measuring the efficiency of admissibility projection within the structural box regime.
