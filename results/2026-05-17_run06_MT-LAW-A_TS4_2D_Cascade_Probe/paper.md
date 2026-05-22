# Technical Paper: MT-LAW-A TS4 2D Cascade Probe

## 0. Metadata
```json
{
  "claim_id": "MT-LAW-A-TS4-006",
  "status": "L1",
  "classification": "Proposed Interpretation",
  "charter_classification": "provisional",
  "models_used": ["rd_moving_boundary_sim_v1_cpp"],
  "model_classes": ["pde"],
  "seeds_used": 1,
  "falsification_run": false,
  "recoverable_outputs": [
    "results/2026-05-17_run06_MT-LAW-A_TS4_2D_Cascade_Probe/data/"
  ],
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

## 1. Abstract
The Mono-Process Framework is founded on the principle that distinguishability and continuation are inseparable aspects of one recursive process, encoded as (ℰ≠0) ⇔_x δ(ℰ>0). Within these models, this campaign investigates the propagation of activity cascades in a 2D Reaction-Diffusion system with moving boundaries. We observe that activity propagates across the domain in a wave-like "cascade" only when the local trigger threshold is exceeded, consistent with the framework's internal gating logic.

## 2. Scope
This study investigates the propagation of activity cascades in a 2D Reaction-Diffusion system with moving boundaries. The focus is on the "Turbo Mode" trigger thresholds (tg) ranging from 0.1 to 1.0. Results are confined to a single seed (42) and the specific moving-boundary PDE implementation used in the simulation.

## 3. Direct Observation and Definition
In the simulation data, we observe that activity propagates across the domain in a wave-like "cascade" only when the local trigger threshold tg is exceeded by the relational mismatch (ℰ). This onset is defined as a "propagation event," where the continuation of one node induces a sufficient mismatch in its neighbors to trigger their own continuation.

## 4. Framework-Internal Inference
The framework interprets this cascade as a chain of recursive (ℰ≠0) ⇔_x δ(ℰ>0) events. Each successful continuation δ(ℰ>0) generates a new residue R which, via coupling (CSI), manifests as update pressure ℰ for adjacent nodes, thereby sustaining the process flow across the lattice.

## 5. External Structural Resemblance (Analogy)
This behavior structurally resembles forest fires, avalanches, or action potential propagation in neurons. These external phenomena are treated as formal analogies for the underlying process recursion.

## 6. Non-Proof and Limits
This study does NOT prove that physical waves or biological signals are governed by this specific framework. It only demonstrates that the framework can simulate cascade phenomena within a moving-boundary PDE approximation. The use of a single seed (L1) means the stochastic robustness of these cascades remains unverified.

## 7. Failure Modes and Uncertainty
Single seed (42) usage limits the results to a single deterministic trace; stochastic variability in trigger sensitivity is not yet characterized. The moving-boundary implementation may introduce numerical artifacts near the domain limits that do not reflect the core process logic.

## 8. Experimental Setup
- **Tool:** `rd_moving_boundary_sim_v1_cpp` (C4 certified)
- **Configuration:** 2D grid with moving boundaries.
- **Parameters:** tg (turbo trigger threshold) ∈ [0.1, 1.0].
- **Seeds:** [42].

## 9. Observables
```json
{
  "cascade_velocity": "propagation_speed_across_lattice",
  "peak_amplitude": "maximum_active_residue",
  "normalization": "none"
}
```

## 10. Results
Data from the turbo mode sweep shows a sharp transition in cascade behavior at tg = 0.4. Below this threshold, activity propagates as a sustained wave front. Above this threshold, activity becomes localized or fails to propagate, indicating where the relational barrier k outstrips the coupling reach.

## 11. Cross-Model Comparison
None performed in this run. Reference implementation `sim.py` was used for logic verification only.

## 12. Falsification
None explicitly recorded in the run manifest. Future runs require FV-1 (Mechanism Substitution) across different lattice topologies.

## 13. Classification
- **Proposed Interpretation (L1):** The observed propagation is consistent with the framework's theory, but the reliance on a single model class and single seed prevents a higher classification.

## 14. Conclusion
Within these models, the propagation of activity is gated by a local relational threshold consistent with the (ℰ≠0) ⇔_x δ(ℰ>0) rule. The observation of discrete cascade onset demonstrates that the Mono-Process Framework can model complex propagation phenomena through simple recursive rules, although further multi-seed validation is required to characterize the stability of these waves.
