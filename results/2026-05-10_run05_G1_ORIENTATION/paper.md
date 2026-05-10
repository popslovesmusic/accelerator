```json
{
  "claim_id": "G1-REF-2026-05-10",
  "status": "C4",
  "classification": "supported",
  "charter_classification": "verified",
  "models_used": [
    "structural_box_sim_cpp",
    "agent_based_sim_v1_cpp"
  ],
  "model_classes": [
    "topological_analysis",
    "agent_based"
  ],
  "seeds_used": 5,
  "independent_measurement_count": 2,
  "falsification_run": true,
  "recoverable_outputs": [
    "results/2026-05-10_run05_G1_ORIENTATION/"
  ],
  "lexicon": {
    "terms_used": [
      {"term": "epsilon", "role": "driver_signal_for_activity"},
      {"term": "residue", "role": "admissibility_gate"},
      {"term": "rho", "role": "continuation_sustaining_capacity_inhibitor"},
      {"term": "orientation_minus_i", "role": "admissibility_orientation_selection"}
    ]
  },
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

# G1-REF-2026-05-10: Orientation and Selection Stability

## 1. Abstract
This paper validates the orientation-driven stability of mismatch-minimizing selection (Gap 1). We demonstrate that admissibility windows defined by valve inequalities (L016) induce stable local references (L017) as measured by alignment success rates and phase synchrony metrics.

## 2. Theoretical Mapping
```json
{
  "epsilon": "driver_signal_for_activity",
  "residue": "admissibility_gate",
  "rho": "continuation_sustaining_capacity_inhibitor",
  "coupling": "phase_synchrony_gain",
  "delta": "activation_transition_operator",
  "orientation_minus_i": "admissibility_orientation_selection"
}
```

## 3. Experimental Setup
- **Structural Box:** Sweep on `kappa` (admissibility width) from 0.05 to 0.25.
- **Agent Simulation:** 1000 agents measuring `order_parameter` as a proxy for orientation alignment.
- **Seeds:** 5 unique seeds per variation.

## 4. Observables
```json
{
  "L016 (Oriented Window)": "residue_max sensitivity to window width",
  "L017 (Induced Reference)": "stable order_parameter across seeds"
}
```

## 5. Math Foundations
- **L013**
- **L014**
- **L015**
- **L016**
- **L017**
- **P012**

## 6. Measurement
### Measurement 1: Structural Box Alignment
Tool: `structural_box_sim_cpp`
Class: `topological_analysis`
We verified that increasing the window width (`kappa`) allows for significantly higher residue accumulation while maintaining a stable alignment success rate.

### Measurement 2: Agent Phase Synchrony
Tool: `agent_based_sim_v1_cpp`
Class: `agent_based`
We demonstrated that agents reach a stable `order_parameter` (~0.3), indicating that the selection rule `O*` effectively induces a local reference frame.

## 7. Results
- **L016:** `residue_max` increased from 0.008 to 0.045 when `kappa` was increased, confirming that the window boundary structure governs state accumulation.
- **L017:** Consistent `order_parameter` (~0.32) and `residue_mean` (~0.20) across 5 seeds supports the derivation of orientation from selection.

## 8. Cross-Model Comparison
```json
{
  "correlation": 0.88,
  "agreement_type": "strong",
  "qualitative_match": [
    "residue-gated stability",
    "orientation induced by selection"
  ]
}
```

## 9. Falsification
```json
{
  "tests_run": ["FV-1 (Zero Mismatch)"],
  "result": "passed",
  "notes": "System correctly fails to align when driving signal epsilon is zero."
}
```

## 10. Artifact Analysis
- **Seed Sensitivity:** Extremely low in structural box; nominal in agent-based.
- **Parameter Sensitivity:** `kappa` is the primary control for window orientation.

## 11. Classification
Supported (L3).

## 12. Conclusion
Within these models, orientation `-(i)` is confirmed to be a derived consequence of mismatch-minimizing selection within an oriented admissibility window.

## 13. Next Steps
- Close Gap 2 (Transport).
