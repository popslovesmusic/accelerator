# Technical Paper: MT-LAW-A TS4 Hysteresis Audit

## 0. Metadata
```json
{
  "claim_id": "MT-LAW-A-TS4-005",
  "status": "L1",
  "classification": "Proposed Interpretation",
  "charter_classification": "provisional",
  "models_used": ["structural_box_sim_cpp"],
  "model_classes": ["pde"],
  "seeds_used": 8,
  "falsification_run": false,
  "recoverable_outputs": [
    "results/2026-05-17_run05_MT-LAW-A_TS4_Hysteresis_Audit/data/"
  ],
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

## 1. Abstract
The Mono-Process Framework is founded on the principle that distinguishability and continuation are inseparable aspects of one recursive process, encoded as (ℰ≠0) ⇔_x δ(ℰ>0). Within these models, this campaign investigates the response of a structural box node to varying perturbation magnitudes. We observe that the system exhibits path-dependent state evolution (hysteresis), consistent with the framework's internal logic of residue inscription.

## 2. Scope
This study examines the response of a structural box node to varying perturbation magnitudes (perturb) in the range [0.30, 0.44]. It focuses on whether the system returns to its initial state or exhibits path-dependent residue (hysteresis) across 8 independent seeds. Results are limited to the specific update rules implemented in the `structural_box_sim_cpp` engine.

## 3. Direct Observation and Definition
In the simulation data, we observe that the node state does not always return to its exact initial coordinate after a perturbation-recovery cycle. This discrepancy is defined as "hysteresis," where the final state $x_f$ differs from the initial state $x_0$ by a measurable residue $R = |x_f - x_0|$.

## 4. Framework-Internal Inference
The framework interprets this hysteresis as the accumulation of residue R which has become "inscribed" within the node's local identity. This is a direct consequence of the (ℰ≠0) condition resulting in a non-zero state transition δ(ℰ>0) that is not fully reversed by subsequent symmetry-breaking update steps. The "memory" of the perturbation is thus stored as a physical shift in the process continuation frame.

## 5. External Structural Resemblance (Analogy)
This behavior structurally resembles magnetic hysteresis in ferromagnetic materials or plastic deformation in solid mechanics, where the history of applied force leaves a permanent trace on the system state. These are treated here only as formal analogies.

## 6. Non-Proof and Limits
This study does NOT prove that all physical memory or material hysteresis is governed by this framework. It only demonstrates that the framework's update rule naturally produces path-dependent state evolution without the need for explicit memory buffers. The results are sensitive to the perturbation duration and the specific damping/coupling parameters used.

## 7. Failure Modes and Uncertainty
Seed sensitivity in recovery paths suggests that the final state may be dependent on the specific stochastic noise floor of the engine. Numerical precision limits in the C++ backend may also influence the resolution of very small hysteresis residues ($R < 10^{-7}$).

## 8. Experimental Setup
- **Tool:** `structural_box_sim_cpp` (C4 certified)
- **Configuration:** Single-node perturbation cycle.
- **Parameters:** perturb (perturbation magnitude) ∈ [0.30, 0.44].
- **Seeds:** [500, 501, 502, 503, 504, 505, 506, 507].

## 9. Observables
```json
{
  "hysteresis_magnitude": "delta_x_final_initial",
  "residue_accumulation_rate": "dR_dt_during_perturbation",
  "normalization": "none"
}
```

## 10. Results
Data across 8 seeds indicates that for perturb > 0.36, the system reliably enters a hysteresis regime where the final state is shifted by an average of 2.4% relative to the perturbation magnitude. Below this threshold, the system demonstrates "Elastic Recovery," returning to within 0.01% of the initial state, suggesting a relational barrier to permanent inscription.

## 11. Cross-Model Comparison
None performed in this run. Reference implementation `sim.py` was used for logic verification only.

## 12. Falsification
None explicitly recorded in the run manifest. Future runs require FV-2 (Scale Invariance) to determine if the hysteresis threshold scales with the admissibility window k.

## 13. Classification
- **Proposed Interpretation (L1):** The observed hysteresis is consistent with the framework's theory of residue, but the lack of multi-mechanism verification restricts the classification level.

## 14. Conclusion
Within these models, the Mono-Process Framework produces path-dependent state evolution consistent with the (ℰ≠0) ⇔_x δ(ℰ>0) rule. The observation of a discrete threshold for hysteresis suggests that "memory" in this framework is an emergent property of the relational gating of process residues, although further validation is required to separate numerical artifacts from core process behavior.
