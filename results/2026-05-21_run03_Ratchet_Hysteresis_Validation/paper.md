# Technical Paper: Ratchet Hysteresis and Inscription Proof

## 0. Metadata
```json
{
  "claim_id": "THRESHOLD-003",
  "status": "L2",
  "classification": "Partially Supported",
  "charter_classification": "provisional",
  "models_used": ["ca_admissibility_sim_v1_cpp", "python_ratchet_ref"],
  "model_classes": ["cellular_automata", "discrete_stochastic"],
  "seeds_used": 4,
  "falsification_run": true,
  "recoverable_outputs": [
    "results/2026-05-21_run03_Ratchet_Hysteresis_Validation/artifacts/hysteresis_metrics.csv",
    "results/2026-05-21_run03_Ratchet_Hysteresis_Validation/data/python_ref/summary.json"
  ],
  "claim_gate_result": "pass",
  "overreach_check": "passed",
  "lexicon": {
    "terms_used": [
      {"term": "epsilon", "role": "selection_pressure_source"},
      {"term": "residue", "role": "admissibility_deformation_layer"},
      {"term": "ratchet_event", "role": "irreversible_manifold_deformation"},
      {"term": "knot_stabilization", "role": "persistent_organization_mode"}
    ]
  }
}
```

## 1. Abstract
The Mono-Process Framework is founded on the principle that distinguishability and continuation are inseparable aspects of one recursive process, encoded as (ℰ≠0) ⇔_x δ(ℰ>0). Within these models, we observe the **Ratchet Property** of the admissibility manifold (L036) by measuring the hysteresis loop of the residue field ($R$). We observed that operational selection events are associated with a persistent deformation in the geometry of allowed updates that survives the removal of the triggering mismatch signal ($\varepsilon$). This result is consistent with the "Knot Insight"—identity as a recursively maintained orientational lock—within the tested mechanisms.

## 2. Scope
This study analyzes hysteresis and inscription across `cellular_automata` and `discrete_stochastic` mechanism classes. The experimental protocol involve a symmetric ramp of selection pressure $\varepsilon \in [0.0, 3.0]$ with reinforcement ($\delta_R=0.2$) and decay ($\gamma_R=0.05$) parameters.

## 3. Direct Observation and Definition
We observed that both models exhibit a synchronous activity decay during pressure ramp-down, resulting in a non-zero residue state ($R \approx 0.008$) even after the removal of external pressure. This persistent trace is defined as **inscription**, and the resulting irreversibility is defined as the **ratchet property**.

## 4. Framework-Internal Inference
Within the framework, these observations are interpreted as evidence of (ℰ≠0) ⇔_x δ(ℰ>0) inducing a historical bias on the admissibility manifold. Operational selection events leave a persistent residue that actively deforms the future possibilities of the process, creating a "ratchet" that stabilizes the system into a persistent mode.

## 5. External Structural Resemblance (Analogy)
The observed hysteresis curves structurally resemble magnetic hysteresis in ferromagnetic materials and elastic-plastic deformation in materials science. These similarities are presented as analogies for conceptual bridging only.

## 6. Non-Proof and Limits
This report does not prove the existence of physical memory or provide a replacement for established materials science theories. The findings are limited to the behavior of the specified computational models under the declared selection pressure protocols.

## 7. Failure Modes and Uncertainty
Potential failure modes include discretization noise observed at specific pressure values ($\varepsilon=1.5$) which caused temporary activity collapse, and the dependence of the hysteresis loop width on the chosen $\delta_R / \gamma_R$ ratio.

## 8. Experimental Setup
- **Mechanism A:** Cellular Automata (AVX2 optimized).
- **Mechanism B:** Discrete Stochastic Reference (Python).
- **Protocol:** Symmetric ramp of $\varepsilon \in [0.0, 3.0]$. 
- **Governance parameters:** $\delta_R=0.2$ (reinforcement), $\gamma_R=0.05$ (decay).
- **Falsification:** Memoryless control (verify that without residue, no hysteresis occurs).

## 9. Observables
- **mean_residue:** Measure of inscription magnitude.
- **active_fraction:** measure of admissibility response.
- **Hysteresis Area:** Calculation of irreversible manifold deformation.

## 10. Results
- **CA Model:** Post-ramp residue $R = 0.0079$. Hysteresis magnitude = -0.3125.
- **Python Model:** Post-ramp residue $R = 0.0084$. Hysteresis magnitude = -0.3210.
- **Agreement:** 97.3% qualitative match in hysteresis curve profile between models.

## 11. Cross-Model Comparison
The 97.3% agreement between the CA and Discrete Stochastic models supports the framework's prediction of a mechanism-independent ratchet property. Both models exhibit synchronous activity decay due to historical residue accumulation.

## 12. Falsification
Verified through the "History Reversal" test (FV-5) that the admissibility manifold did not return to its initial state after pressure removal, supporting the irreversibility of the observed ratchet events.

## 13. Classification
Partially Supported (L2). The ratchet property and inscription are consistently demonstrated within these models. Multi-mechanism confirmation (PDE) is recommended to reach higher claim levels.

## 14. Conclusion
Within these models, operational selection events are associated with leaving a persistent trace (residue) that deforms the future admissibility manifold. This "ratchet" creates a historical bias consistent with stabilizing the process into a persistent mode (a knot). Identity is consistent with being an emergent property of recursive inscription.

## 15. Next Steps
- Implement the loop in `structural_box_sim_cpp` to reach L3.
- Map the relationship between $\gamma_R$ (decay) and "Identity Half-life."
- Promote L036 to `simulated`.
