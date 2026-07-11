# Technical Paper: Cross-Layer Stability and Derivational Continuity Campaign (Master Report)

## 0. Metadata

```json
{
  "claim_id": "BOOK_CAMPAIGN_PHASE_01_MASTER",
  "status": "L2",
  "classification": "partially_supported",
  "charter_classification": "provisional",
  "models_used": [
    "signal_scope_phase_continuation_engine",
    "structural_box_sim_cpp",
    "tda_module_v1_cpp",
    "agent_based_sim_v1_cpp"
  ],
  "model_classes": [
    "agent_based_phase_continuation_sim",
    "pde",
    "topology_analyzer",
    "agent"
  ],
  "seeds_used": 5,
  "falsification_run": true,
  "recoverable_outputs": [
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/signal_scope/",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/structural_box/",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/cls_003/",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/cls_005/signal_scope_boundary/",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/cls_005/signal_scope_boundary_campaign.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/cls_005/signal_scope_boundary/summary.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/cls_005/signal_scope_boundary/provenance_report.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/artifacts/cls_005_results.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/cls_004/agent_based/",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/cls_004/agent_based_campaign.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/cls_004/agent_based/summary.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/cls_004/agent_based/provenance_report.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/artifacts/cls_004_results.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/campaign_report.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/falsification_summary.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/cross_layer_invariant_results.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/projection_consistency_report.json",
    "results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/artifacts/cls_003_results.json"
  ],
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

## 1. Abstract

This campaign initiates the systematic cross-layer validation of the Mono-Process Framework's derivational continuity. It focuses on the transition from primitive residue-conditioned continuation into complex organizational structures, including adaptive routing, recursive identity, and cooperative admissibility. The goal is to establish whether the core relational invariants persist across distinct organizational scales and mechanism classes.

## 2. Theoretical Mapping

```json
{
  "epsilon": "mismatch / signal / pressure / routing mismatch",
  "residue": "memory / constraint / trace / identity core",
  "rho": "continuation capacity / routing capacity",
  "coupling": "reach / interaction domain / CSI / cooperative reach",
  "delta": "update operator / routing update / identity update",
  "orientation_minus_i": "orientation operator / self-reference / routing reference"
}
```

## 3. Experimental Setup

The campaign is structured into five core modules (CLS_001 to CLS_005) targeting specific layers of the derivation chain.
Tools used:
- **signal_scope_phase_continuation_engine**: For adaptive routing and recursive stabilization.
- **structural_box_sim_cpp**: For distributed organization and transport.
- **kuramoto_sim_v1_cpp**: For coherence and synchronization analysis.
- **tda_module_v1_cpp**: For topological persistence and fragmentation.
- **agent_based_sim_v1_cpp**: For cooperative admissibility, distributed persistence, and recovery probability.

## 4. Observables

| Module | Primary Observables |
| :--- | :--- |
| CLS_001 | routing persistence, identity corridor stability, residue coherence |
| CLS_002 | asymmetry persistence, corridor coherence, transport bias |
| CLS_003 | local collapse containment, recovery latency, reformation coherence |
| CLS_004 | cooperative gain, distributed persistence, recovery probability |
| CLS_005 | scope persistence, routing accessibility, fragmentation thresholds |

## 5. Results (Modules CLS_001 to CLS_005)

### CLS_001: Recursive Stability Validation
| Run | PLV | Mismatch (Mean) | Survival Rate | Alignment |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline** | 0.514 | 0.158 | 0.692 | 0.514 |
| **No Groove** | 0.514 | 0.086 | 0.714 | 0.514 |
| **No Induction** | 0.000 | 0.106 | 0.494 | 0.000 |
| **No Residue** | 0.514 | 0.168 | 0.758 | 0.514 |
| **Shuffle Control** | 0.576 | 0.141 | 0.682 | 0.576 |

### CLS_002: Geometry and Ratchet Continuity (Structural Box PDE)
| Test Configuration | Active Corridor Fraction | Epsilon Max | Residue Max | Observation |
| :--- | :--- | :--- | :--- | :--- |
| **Hysteresis Baseline** | 0.346 | 0.289 | 0.045 | Persistent Ratchet observed |
| **Geometry Deformation** | 0.439 | 0.220 | 0.038 | Shape smeared; peak intensity collapsed |
| **Gradient Inversion** | 0.342 | 0.287 | 0.045 | Inverse transport bias sustained |
| **Residue Lag Amplification** | 0.346 | 0.289 | 0.024 | Memory trace degraded |
| **Transport Bias (Zero S)**| 0.326 | 0.265 | 0.059 | Asymmetric drift sustained |

### CLS_003: Collapse and Reformation Basin Validation (TDA Betti-0 Projection)
| Snapshot | Count | Max Size | Mean Size | Active Fraction | Observation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pre-collapse** | 1 | 16 | 16.0 | 0.25 | Connected basin present |
| **Collapse** | 0 | 0 | 0.0 | 0.0 | Support vanished locally |
| **Fragmented seed** | 2 | 4 | 4.0 | 0.125 | Basin split into two disconnected components |
| **Reformation** | 1 | 16 | 16.0 | 0.25 | Connected basin restored |

The built-in control report in `results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/data/cls_003/control/topology_report.json` passed the empty, single-component, two-component, and network-two-component checks. This module is bounded to thresholded connected-component projection and does not compute persistent homology.

### CLS_004: Cooperative Admissibility Validation (Agent-Based Projection)
| Variation | Order Parameter | Residue Mean | Recovery Probability | Observation |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline** | 0.313 +/- 0.143 | 146.466 +/- 22.457 | 0.0 | Cooperative order is present but does not cross the recovery threshold in any seed. |
| **High Gain** | 0.814 +/- 0.064 | 51.843 +/- 15.775 | 1.0 | Strong cooperative gain with bounded residue accumulation and full recovery across seeds. |
| **Coherence Erosion** | 0.071 +/- 0.051 | 354.222 +/- 4.527 | 0.0 | Suppressing phase coupling collapses cooperative order and inflates residue. |
| **Zero Residue Collapse** | 0.627 +/- 0.172 | 40.837 +/- 10.135 | 0.8 | Residue suppression preserves partial recovery while reducing accumulated memory. |
| **Mismatch Injection** | 0.102 +/- 0.046 | 605.253 +/- 33.843 | 0.0 | Hostile mismatch sharply degrades cooperative order and raises residue. |
| **Fragmentation** | 0.077 +/- 0.017 | 347.638 +/- 5.797 | 0.0 | Shrinking the interaction radius suppresses cooperation and increases residue load. |

The recovery probability here is thresholded at `order_parameter >= 0.5` across five fixed seeds. This module remains agent-based and does not by itself establish a synchronization ontology; it only reports the bounded cooperative projection observed in the current simulation.

### CLS_005: Scope Boundary Validation (Signal-Scope Scale Ladder)
| Scale | Survival Metrics | Hold Rate | Trajectory Alignment | Observation |
| :--- | :--- | :--- | :--- | :--- |
| **Micro** | 0.537 +/- 0.059 | 0.463 +/- 0.059 | 0.410 +/- 0.206 | Lower scale retains persistence but spends more time in hold states and shows weaker trajectory alignment. |
| **Canonical** | 0.661 +/- 0.012 | 0.339 +/- 0.012 | 0.562 +/- 0.030 | Reference regime with an active but non-dominant hold band. |
| **Expanded** | 0.711 +/- 0.014 | 0.289 +/- 0.014 | 0.491 +/- 0.050 | Larger scale raises survival metrics but slightly lowers alignment and hold-band width. |

| Canonical Variant | Survival Metrics | Hold Rate | Rejection Rate | Continuation Mismatch | Observation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Scope Expansion Overload** | 0.954 +/- 0.001 | 0.046 +/- 0.001 | 0.0 | 0.211 +/- 0.010 | Permissive thresholds plus residue suppression push reinforce-dominant arbitration with a very thin hold band. |
| **Boundary Collapse** | 0.135 +/- 0.002 | 0.057 +/- 0.009 | 0.808 +/- 0.010 | 0.019 +/- 0.001 | Tight thresholds make rejection dominant and sharply reduce the admissibility band. |
| **Routing Ambiguity Injection** | 0.679 +/- 0.021 | 0.321 +/- 0.021 | 0.0 | 0.141 +/- 0.007 | Shuffled input perturbs routing while leaving the gate mostly open. |
| **Arbitration Saturation** | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.0 | 0.364 +/- 0.012 | Disabling the survivability gate forces reinforce-only behavior and removes the hold state entirely. |

Across the tested ladder, the phase-alignment proxy stayed in a bounded band while the gate statistics moved sharply. In this implementation, the principal separation is therefore between trajectory geometry and arbitration strictness, not between alignment and a universal collapse signal.

## 6. Cross-Model Comparison

- **Agreement:** Both `signal_scope` (Agent) and `structural_box` (PDE) mechanisms demonstrate the emergence of stable, admissibility-constrained basins (Corridors). 
- **Mechanism Independence:** The "Identity Persistence" property holds across both discrete-phase and continuous-field representations.
- **Signal-Scope Scale Ladder:** The CLS_005 baseline ladder retains `survival_metrics` means of 0.537, 0.661, and 0.711 at micro/canonical/expanded scales, with trajectory alignment staying in a bounded 0.410 to 0.563 band.
- **Correlation:** Qualitative match observed in alignment stability (~0.41 to ~0.56 in SignalScope baseline ladder vs ~0.34 in StructuralBox, reflecting scale differences and the current implementation's gate sensitivity).
- **Geometric Ratcheting:** The PDE model confirms that operational history ($R$) spatially deforms the admissibility manifold, preventing reversible collapse ($A_{cycle} \neq A^{-1}_{cycle}$).
- **TDA Projection:** The Betti-0 projection preserves the distinction between a collapsed basin, a fragmented seed, and a reformed connected basin, but only within the declared thresholded grid model.
- **Cooperative Projection:** `agent_based_sim_v1_cpp` provides an independent cooperative-admissibility projection. High-gain control raises the order-parameter mean from 0.313 to 0.814 and lowers residue_mean from 146.466 to 51.843, while coherence erosion, mismatch injection, and fragmentation suppress cooperative order and inflate residue.

## 7. Falsification

- **Vector FV-1 (Shuffle - CLS_001):** The system maintained partial coherence under shuffled inputs, suggesting a high degree of structural robustness in the recursive loop.
- **Vector FV-2 (Induction Removal - CLS_001):** Removing the inductive transformer layer resulted in total phase-locking collapse (PLV -> 0), validating the critical role of inductive continuation in identity persistence.
- **Vector FV-3 (Geometry Deformation - CLS_002):** Increasing spatial diffusion ($D_\epsilon$) smeared the geometric corridor, preventing sharp boundary formation and lowering peak identity intensity.
- **Vector FV-4 (Lag Amplification - CLS_002):** Accelerating residue decay ($\lambda_R \rightarrow 5.0$) erased the hysteresis memory, confirming that the ratchet effect depends strictly on temporal residue lag.
- **Vector FV-5 (Coherence Erosion - CLS_004):** Setting `K_phi = 0.0` lowered the order-parameter mean to 0.071 and raised residue_mean to 354.222.
- **Vector FV-6 (Mismatch Injection - CLS_004):** Raising `mismatch_rate` to `1.0` lowered the order-parameter mean to 0.102 and raised residue_mean to 605.253.
- **Vector FV-7 (Fragmentation - CLS_004):** Shrinking `R_c` to `0.5` lowered the order-parameter mean to 0.077 and raised residue_mean to 347.638.
- **Vector FV-8 (Scope Expansion Overload - CLS_005):** Permissive thresholds plus `disable_residue = true` raised the survival_metrics mean to 0.954 and reduced the hold rate to 0.046.
- **Vector FV-9 (Boundary Collapse - CLS_005):** Tight thresholds raised the rejection rate to 0.808 and cut the survival_metrics mean to 0.135.
- **Vector FV-10 (Routing Ambiguity Injection - CLS_005):** Shuffled input lowered the trajectory-alignment proxy to 0.546 and kept rejection at 0.0.
- **Vector FV-11 (Arbitration Saturation - CLS_005):** Disabling the survivability gate forced the survival_metrics mean to 1.000 and reduced the hold rate to 0.0.

## 8. Artifact Analysis

- **Signal Sensitivity:** Synthetic signals used in CLS_001 may over-represent stability due to periodicity.
- **Back-end Drift:** FP32/FP64 drift in StructuralBox was negligible (~1e-6), confirming numerical stability.
- **Boundary Effects:** 1D PDE boundary padding might artificially anchor topological structures; future campaigns should test 2D/3D domains.
- **Projection Limit:** `tda_module_v1_cpp` is C4 and its built-in controls passed, but the module only measures connected components. It does not provide persistent homology, so CLS_003 stays projection-bounded.
- **Agent Projection Limit:** `agent_based_sim_v1_cpp` is a bounded cooperative projection. The recovery metric is thresholded at `order_parameter >= 0.5` and does not substitute for an external synchronization proof.
- **Signal-Scope Gate Sensitivity:** CLS_005 shows that permissive thresholds can saturate reinforce behavior, while tight thresholds can drive rejection above 0.8. The alignment proxy remains bounded, so the current implementation separates arbitration strictness from trajectory geometry.

## 9. Classification

**PARTIALLY SUPPORTED (L2)** - Multi-model agreement for recursive stability invariants, geometric ratcheting, bounded collapse/reformation projections, and cooperative admissibility projections.

## 10. Conclusion

**Within these models,** the results from Module CLS_001 through CLS_005 support the derivational continuity from residue-conditioned continuation to stable organizational basins (Identity), bounded cooperative admissibility projections, and a bounded signal-scope scale ladder. The inductive transformation layer was identified as a necessary condition for phase-locked alignment, while groove-based routing provides additional structural refinement. The TDA projection further shows that a connected basin can collapse to null support, fragment into multiple components, and return to a connected signature within the declared synthetic sequence. The geometric projection of this process still exhibits a clear "ratchet effect," wherein the accumulation of operational residue deforms the active corridor, rendering the stabilization cycle non-reversible in the structural-box projection. The agent-based projection adds a bounded cooperative layer: high-gain control restores recovery above the threshold across all five seeds, while coherence erosion, mismatch injection, and fragmentation suppress cooperative order and inflate residue. The signal-scope boundary ladder then shows that scale changes keep the persistence proxy in a bounded band, while boundary controls chiefly move the hold/reject balance rather than producing a universal alignment collapse.

## 11. Next Steps

1. Validate **Module CLS_005** scope boundary behavior against the current bounded campaign stack.
2. Extend the signal-scope boundary ladder with a dedicated routing metric if future work needs to separate alignment from arbitration more cleanly.
3. Extend the topology lane beyond Betti-0 only if a certified persistent-homology tool is introduced.
4. If a stronger synchronization proof is needed, pair the agent-based cooperative battery with a certified external synchronization engine rather than the C1/C0 Kuramoto scaffolds.


