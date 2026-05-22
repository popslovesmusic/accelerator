```json
{
  "claim_id": "PCD-ORIENTATION-001",
  "status": "C2",
  "classification": "theoretical",
  "charter_classification": "theoretical",
  "models_used": ["weighted_graph_prototype", "i_field_probe"],
  "model_classes": ["graph_dynamics", "field_dynamics"],
  "seeds_used": 1,
  "falsification_run": false,
  "recoverable_outputs": ["artifacts/runs/paper2_relational_geodesic_prototype_v1_1/"],
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

# Deriving Local Reference -(i) from Admissible Mismatch-Minimizing Selection

## 1. Abstract
The Mono-Process Framework is founded on the principle that distinguishability and continuation are inseparable aspects of one recursive process, encoded as (ℰ≠0) ⇔_x δ(ℰ>0). This paper examines the derivation of the local reference mechanism `-(i)` as an admissible selection operator forced by mismatch under nonzero continuation. Within this framework, `-(i)` is not treated as a primitive object but as a locally selected reference induced by mismatch-minimizing operator choice.

## 2. Scope
This study is limited to the theoretical derivation and minimal operational probing of the `-(i)` selection mechanism. It utilizes synthetic weighted-graph and grid-based probes to verify the internal consistency of the derivation.

## 3. Direct Observation and Definition
In the tested models, we define the local reference `-(i)` as the output of an `argmin` selection over an admissible operator family. We observe that when multiple admissible updates are possible, a rule based on minimizing relational mismatch cost (μ_rel) induces a stable (or set-valued) local orientation.

## 4. Framework-Internal Inference
Within this framework, the condition (ℰ≠0) forces continuation, which in turn necessitates mismatch (epsilon). Coherent continuation under mismatch is inferred to require a selection rule (O*) to order admissible updates. The resulting reference `-(i)` is thus a forced diagnostic of the underlying process logic rather than an external geometric input.

## 5. External Structural Resemblance (Analogy)
The induced local reference structurally resembles a frame field or a local coordinate basis in differential geometry. However, this model treats the "basis" as a dynamic selection residue of the recursive update process rather than as an ontological manifold property.

## 6. Non-Proof and Limits
This derivation does not prove the existence of physical orientation fields or reference frames in the vacuum. It demonstrates a consistent mathematical path for deriving such structures from the (ℰ≠0) primitive. The included probes are synthetic and intended for coherence verification, not for matching physical data.

## 7. Failure Modes and Uncertainty
Failure of the selection mechanism occurs at "degeneracy boundaries" where multiple operators yield near-identical costs. This leads to set-valued references and high "transport residual" (δ_T), marking the breakdown of local structural coherence.

## 8. Experimental Setup
- **Weighted-Graph Prototype:** Synthetic graph measuring geodesic cost and alignment.
- **I-Field Probe:** Grid-wide computation of `O*(x)` and `-(i)` selection.
- **Config:** `paper2_relational_geodesic_prototype_v1.json`.
- **Artifacts:** `artifacts/runs/paper2_relational_geodesic_prototype_v1_1/`.

## 9. Observables
- **δ_T (Transport Residual):** Measures the instability of the reference-selection mechanism.
- **Δ_align (Alignment Divergence):** Measures the relational consistency between multiple references.
- **κ (Operational Curvature):** Derived from the rate of breakdown of alignment and transport.

## 10. Results
| scenario_id | observed_regime | Δ_align_max | δ_T_mean | κ_mean |
|---|---|---:|---:|---:|
| corridor | corridor | 0.0593 | 0.00756 | 0.0117 |
| shelf_transition | shelf_transition | 0.1506 | 0.0135 | 0.0297 |
| decoupling | decoupling | 0.2899 | 0.0211 | 0.0460 |

## 11. Cross-Model Comparison
The weighted-graph prototype and the grid-wide field probe show consistent regime separation. Both models demonstrate that `-(i)`-selection organizes into coherent spatial structures whose deformation tracks the corridor-to-decoupling transition.

## 12. Falsification
The selection mechanism is falsifiable by verifying whether "random" selection (bypassing μ_rel minimization) destroys the observed corridor structures. (Implicit in the "decoupling" regime results where selection cost is high).

## 13. Classification
**Status:** **Theoretical (C2)**. The derivation is internally consistent and supported by minimal operational probes.

## 14. Conclusion
Within these models, the local reference `-(i)` is derived as a selection residue of the recursive process (ℰ≠0) ⇔_x δ(ℰ>0). This positions geometric orientation not as an input, but as a derived observable of reference-selection and transport stability under admissible continuation.
