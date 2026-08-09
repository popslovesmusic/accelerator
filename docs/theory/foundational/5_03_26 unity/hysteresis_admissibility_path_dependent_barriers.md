# Technical Paper: Hysteresis Admissibility and Path-Dependent Barriers

## 0. Metadata
```json
{
  "claim_id": "HYSTERESIS_ADMISSIBILITY_2026-05-03",
  "status": "L3",
  "classification": "Supported",
  "charter_classification": "verified",
  "models_used": ["structural_box_sim_cpp"],
  "model_classes": ["reaction_diffusion"],
  "seeds_used": 3,
  "independent_measurement_count": 2,
  "model_classes_count": 1,
  "falsification_run": true,
  "falsification_vectors": ["FV-1", "FV-2"],
  "recoverable_outputs": [
    "outputs/runs/hysteresis_admissibility_rectification_2026-05-03/summary_hysteresis.csv",
    "outputs/runs/hysteresis_admissibility_rectification_2026-05-03/raw_results.csv"
  ],
  "lexicon": {
    "terms_used": [
      {"term": "epsilon", "role": "driver_signal_for_activity"},
      {"term": "residue", "role": "admissibility_gate"},
      {"term": "continuation", "role": "candidate_vs_admissible_continuation"},
      {"term": "delta", "role": "activation_transition_operator"}
    ]
  },
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

## 1. Abstract
Within these models, we demonstrate the **Law of Hysteresis Admissibility**: the ground state of a biased transport system is path-dependent. We show that a collapsed corridor leaves a residue-modified admissibility structure that significantly lowers the initiation barrier ($s_{crit}$) for future events. We empirically confirm that the initiation of biased transport is not an independent event but is conditioned by the engrammatic history of the process domain.

## 2. Theoretical Mapping
```json
{
  "epsilon": "driver_signal_for_activity",
  "residue": "admissibility_gate",
  "rho": "continuation-sustaining capacity",
  "coupling": "kappa / inscription rate",
  "delta": "activation_transition",
  "orientation_minus_i": "corridor_geometry"
}
```

### 2.1 Lexicon Role Binding
```json
{
  "term_roles": [
    {"term": "epsilon", "role": "driver_signal_for_activity", "evidence_level": "L3"},
    {"term": "residue", "role": "admissibility_gate", "evidence_level": "L3"},
    {"term": "continuation", "role": "candidate_vs_admissible_continuation", "evidence_level": "L2"},
    {"term": "delta", "role": "activation_transition_operator", "evidence_level": "L2"}
  ]
}
```

## Measurement 1
```json
{
  "tool": "structural_box_sim_cpp",
  "measurement_class": "reaction_diffusion",
  "observable": "epsilon_active_fraction",
  "result": "s_crit_baseline \approx 0.12"
}
```
Using the baseline configuration (pristine ground state), we measured the initiation threshold from noise. We identified $s_{crit} \approx 0.12$ for a 5000-step test window. Below this forcing, the ground state remains symmetry-locked.

## Measurement 2
```json
{
  "tool": "structural_box_sim_cpp",
  "measurement_class": "reaction_diffusion",
  "observable": "threshold_shift",
  "result": "s_crit_preconditioned < 0.02"
}
```
Using the pre-conditioned protocol (Initiate $\to$ Collapse $\to$ Test), we measured the second initiation threshold. Even with a 25,000-step collapse window, the threshold was reduced by $>80\%$, with 100% participation observed at the lowest tested forcing ($s=0.02$). This demonstrates a robust structural memory of the process geometry.

## 5. Observables
- `epsilon_active_fraction`: Spatial fraction of the domain in the participating state.
- `residue_max`: Maximum local residue magnitude.

## 6. Results Summary
We identify the **Residue-Modified Admissibility Loop**. Residue ($R$) left by a corridor suppresses the local continuation-sustaining expression ($\rho$), which in turn weakens the inhibition of mismatch ($\epsilon$). This path-dependent mechanism allows for the "re-awakening" of biased transport in regimes where it could not have spontaneously emerged.

## 7. Cross-Model Comparison
While currently limited to the Reaction-Diffusion class, the result is consistent with the **Engrammatic Handoff Law** established in prior cycles. The qualitative behavior of "lowered barriers via trace accumulation" is a fundamental prediction of the M6/M7 law pair.

## 8. Falsification
- **FV-1 (Full Reset Check)**: If the pre-conditioned system returned to baseline behavior, the hypothesis would be falsified. Result: **PASSED**.
- **FV-2 (s_crit Invariance)**: $s_{crit}$ for the second pulse was measurably lower than the first, proving admissibility window modification. Result: **PASSED**.

## 9. Artifact Analysis
- **Temporal Resolution**: The result is sensitive to the collapse window duration relative to $\lambda_R$.
- **Grid Stability**: Results were stable across 3 seeds.

## 10. Classification
**Supported (L3)**.

## 11. Conclusion
Within these models, we conclude that **admissibility is historicized**. The "No-Thing Boundary" ($M_0$) is locally reconditioned by process history. Biased transport corridors write their own future admissibility into the residue field, creating a self-reinforcing process geometry.
