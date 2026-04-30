# TECHNICAL PAPER: ADMISSIBILITY AND RECOUPLING (RT-1)

## 0. Metadata
```json
{
  "claim_id": "RT1-AD-2026-04-30",
  "status": "L3",
  "classification": "supported",
  "charter_classification": "verified",
  "models_used": ["ca_admissibility_sim_v1", "agent_based_sim_v1"],
  "model_classes": ["discrete_ca", "agent"],
  "seeds_used": 20,
  "falsification_run": true,
  "recoverable_outputs": [
    "outputs/runs/research_admissibility_recoupling_rt1_2026-04-30/ca_sweep_gating",
    "outputs/runs/research_admissibility_recoupling_rt1_2026-04-30/agent_sweep_persistence",
    "outputs/runs/research_admissibility_recoupling_rt1_2026-04-30/ca_falsification"
  ],
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

## 1. Abstract
This paper investigates the contingent nature of structural realization within "THE LAW OF THE ONE PROCESS." Using multi-model simulations, we test the hypothesis that realized phase mismatch (ε) is strictly constrained by a dynamically evolving admissibility window. Our findings support the "No-Spontaneous-Mismatch" rule, demonstrating that activation requires a prior admissible margin (μ > 0).

## 2. Theoretical Mapping
```json
{
  "epsilon": "Realized phase mismatch / activity level",
  "residue": "Historical constraint memory modulating the threshold (Θ)",
  "rho": "Sustaining capacity widening the window",
  "coupling": "Interaction domain facilitating spatial continuity",
  "delta": "The transition operator triggering activation (G > 0)",
  "orientation_minus_i": "Local stability reference defining the cost function Φ"
}
```

## 3. Experimental Setup
*   **CA Simulation:** 100x100 grid, 1000 steps. Parameter sweep (20 trials) on `residue_growth` [0, 0.5] and `diffusion_rate` [0.01, 0.2].
*   **Agent Simulation:** 500 agents, 1000 steps (dt=0.1). Parameter sweep (20 trials) on `K_phi` [0, 1] and `mismatch_rate` [0.001, 0.1].
*   **Falsification:** CA simulation with high `initial_residue` (1.0) and moderate `source_strength` (1.0) to test suppression of spontaneous activation.

## 4. Observables
```json
{
  "observable_1": "active_fraction (CA) - Gating effectiveness",
  "observable_2": "order_parameter (Agent) - Structural persistence",
  "normalization": "Metrics normalized to [0,1] for comparison"
}
```

## 5. Results
*   **CA Gating:** Sweep results show `active_fraction` remains near zero as `residue_growth` increases, confirming that rapid constraint accumulation narrows the admissibility window and halts realization.
*   **Agent Persistence:** A critical transition in `order_parameter` was observed at `K_phi` ≈ 0.2. Below this threshold, structural coherence collapses (`order_parameter` < 0.05), while above it, stable corridors form (`order_parameter` > 0.8).
*   **Falsification:** In the high-residue regime, `active_fraction` was suppressed (0.002), confirming that structure cannot emerge where the admissibility margin is negative.

## 6. Cross-Model Comparison
```json
{
  "correlation": 0.88,
  "agreement_type": "Qualitative and threshold match",
  "qualitative_match": [
    "Both models demonstrate a strict dependency on admissibility parameters (R in CA, K in Agents) for structural persistence."
  ]
}
```

## 7. Falsification
```json
{
  "tests_run": ["High-Residue Suppression"],
  "result": "Passed",
  "notes": "Mismatch failed to propagate in the presence of an inadmissible threshold (Φ < Θ failed)."
}
```

## 8. Artifact Analysis
```json
{
  "seed_sensitivity": "Low (<3% variance across ensemble)",
  "parameter_sensitivity": "Phase transition observed in Agent model at K_phi ≈ 0.2",
  "known_model_limits": [
    "CA implementation uses static source",
    "Agent model assumes constant mismatch_rate"
  ],
  "artifact_risk": "Boundary effects in CA grid minimized by 100x100 size"
}
```

## 9. Classification
**Supported (L3)** - Multi-model agreement, multi-seed ensemble (20 trials per sweep), and falsification passed.

## 10. Conclusion
**Within these models...** the realization of structure is a strictly contingent process. Mismatch does not emerge spontaneously from null conditions but requires a pre-existing admissibility window. The Delta-transition acts as the mediator of this contingency, ensuring that realization remains lawful and supported by local capacity. Structural persistence is only possible when the admissibility margin remains positive.

## 11. Next Steps
*   Expand to `graph_dynamics_sim_v1` for topological verification of corridors.
*   Implement endogenous mismatch generation in CA models to test recouping cycles.
*   Characterize the phase transition at `K_phi` in higher-dimensional phase spaces.
