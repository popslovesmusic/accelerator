PCD-Formal-Stack: v1
Compliance-Charter: v2.3
Claim-Support-Matrix: required
Math-Source-Binding: required

### 0. Metadata
```json
{
  "claim_id": "BIAS_TRANS_2026_05_02",
  "status": "L2",
  "classification": "Proposed Interpretation",
  "charter_classification": "provisional",
  "models_used": [
    "structural_box_sim_cpp",
    "signal_scope_phase_continuation_engine"
  ],
  "model_classes": [
    "reaction_diffusion",
    "agent_based"
  ],
  "seeds_used": 3,
  "falsification_run": true,
  "recoverable_outputs": [
    "outputs/runs/h1_threshold_sweep/",
    "outputs/runs/h2_collapse_signature/",
    "outputs/runs/h2_natural_control/"
  ],
  "independent_measurement_count": 2,
  "falsification_vectors": [
    "FV-1",
    "FV-2"
  ],
  "claim_gate_result": "downgrade",
  "overreach_check": "failed_lexicon_gate",
  "lexicon": {
    "terms_used": [
      {
        "term": "threshold_transition",
        "role": "entry_boundary_detection"
      },
      {
        "term": "stable_selection_regime",
        "role": "persistence_after_entry"
      },
      {
        "term": "non_oscillatory_collapse_signature",
        "role": "collapse_exit_signature"
      }
    ]
  }
}
```

### 1. Abstract
This paper investigates the theoretical proposal that "biased transport" is a forced, residue-supported, orientation-opposed transport corridor in Strict Procedural Monism (SPM). By integrating the NOT-axiom threshold logic with the anchored-scale gravity formalism, we demonstrate through multi-model simulation that: (1) a sharp forcing `threshold_transition` exists for the formation of stable misalignment corridors, and (2) the collapse of such corridors exhibits a distinct `non_oscillatory_collapse_signature`, differentiating them from natural gravitational basin events.

### 2. Theoretical Mapping
```json
{
  "epsilon": "Counter-bias injection / source strength s",
  "residue": "Persistence/memory substrate kappa",
  "rho": "Re-alignment suppression",
  "coupling": "Interaction domain K",
  "delta": "Collapse transition operator",
  "orientation_minus_i": "Local alignment basin"
}
```

### 2.1 Lexicon Role Binding
```json
{
  "term_roles": [
    {
      "term": "threshold_transition",
      "role": "entry_boundary_detection",
      "process_rewrite": "A parameter boundary where bounded -(i) selection changes stability or cardinality.",
      "primitive_basis": [
        "epsilon",
        "residue",
        "orientation_minus_i"
      ],
      "observable": "alignment_success_rate",
      "metric": "alignment_success_rate_jump",
      "evidence_paths": [
        "outputs/runs/h1_threshold_sweep/"
      ],
      "mechanism_classes": [
        "reaction_diffusion",
        "agent_based"
      ],
      "evidence_level": "L2",
      "claim_usage": "proposed_interpretation"
    },
    {
      "term": "stable_selection_regime",
      "role": "persistence_after_entry",
      "process_rewrite": "A regime where bounded -(i) remains uniquely selected after the entry boundary is crossed.",
      "primitive_basis": [
        "epsilon",
        "residue",
        "orientation_minus_i"
      ],
      "observable": "alignment_persistence_duration",
      "metric": "time_above_coherence_threshold",
      "secondary_metric": "late_time_alignment_success_rate",
      "evidence_paths": [
        "outputs/runs/h1_threshold_sweep/"
      ],
      "mechanism_classes": [
        "reaction_diffusion",
        "agent_based"
      ],
      "evidence_level": "L2",
      "claim_usage": "proposed_interpretation"
    },
    {
      "term": "non_oscillatory_collapse_signature",
      "role": "collapse_exit_signature",
      "process_rewrite": "A collapse signature where bounded -(i) selection fails without dominant oscillatory relaxation.",
      "primitive_basis": [
        "delta",
        "rho",
        "orientation_minus_i"
      ],
      "observable": "dominant_power_fraction",
      "metric": "dominant_power_fraction",
      "secondary_metric": "spectral_entropy",
      "control_comparison": "Kuramoto natural basin ringdown",
      "evidence_paths": [
        "outputs/runs/h2_collapse_signature/",
        "outputs/runs/h2_natural_control/"
      ],
      "mechanism_classes": [
        "agent_based",
        "ode_oscillator"
      ],
      "evidence_level": "L2",
      "claim_usage": "proposed_interpretation"
    }
  ]
}
```



### 3. Experimental Setup
We employed two independent mechanism classes for cross-verification:

#### Measurement 1: Structural Box PDE
- **Tool:** `structural_box_sim_cpp`
- **Measurement Class:** `reaction_diffusion`
- **Method:** 11-trial sweep varying source forcing $s \in [0.0, 1.0]$.
- **Objective:** Identify the misalignment threshold $s_{crit}$.

#### Measurement 2: Signal Scope Agent Engine
- **Tool:** `signal_scope_phase_continuation_engine`
- **Measurement Class:** `agent_based`
- **Justification:** This tool provides a unique agent-based phase-continuation implementation not currently available in native C++.
- **Method:** Sudden loss of learned forcing signal (Alpha-tail removed) to simulate bias window collapse.
- **Analysis:** C++ Spectral Analysis of phase-error transients.

### 4. Observables
```json
{
  "alignment_success_rate": "Fraction of steps maintaining structural coherence; used for threshold entry detection.",
  "alignment_success_rate_jump": "Discrete change in alignment_success_rate across source forcing values.",
  "alignment_persistence_duration": "Duration for which alignment remains above the coherence threshold after the entry boundary is crossed.",
  "time_above_coherence_threshold": "Count or fraction of simulation time steps above the chosen coherence threshold.",
  "late_time_alignment_success_rate": "Alignment success rate measured after transient dynamics have passed.",
  "phase_error": "Deviation between oriented and inductive phase.",
  "dominant_power_fraction": "Spectral concentration of collapse signal.",
  "spectral_entropy": "Dispersion of collapse power across the spectrum; secondary test for non-dominant oscillatory relaxation.",
  "normalization": "Z-score scaling across mechanism classes."
}
```

### 5. Results
#### 5.1 Verification of Measurement 1: Entry Boundary and Persistence
Simulation in the Structural Box PDE revealed a categorical transition in `alignment_success_rate` at $s \approx 0.3$. 
- **Sub-threshold ($s < 0.3$):** System remains in a "partially participating" regime (success rate $\approx 0.3-0.4$).
- **Super-threshold ($s \ge 0.3$):** System enters the `stable_selection_regime` (success rate = $1.0$).
For lexicon binding, `threshold_transition` refers only to the entry-boundary jump in alignment behavior, while `stable_selection_regime` refers to persistence after entry and should be evaluated using alignment persistence duration or late-time alignment success rather than the entry jump alone.

| Forcing ($s$) | Alignment Success Rate | Epsilon Max |
| :--- | :--- | :--- |
| 0.0 | 0.316 | 0.295 |
| 0.2 | 0.433 | 0.331 |
| 0.3 | 1.000 | 0.349 |
| 1.0 | 1.000 | 0.473 |

#### 5.2 Verification of Measurement 2: Collapse Signature
Analysis of the `signal_scope` collapse event showed a sharp increase in `phase_error` (from $0.70$ to $1.54$) upon removal of forcing.
- **Spectral Profile:** `dominant_power_fraction` = $0.32$, compared to $0.51$ in natural basin mergers (Kuramoto).
For lexicon binding, `non_oscillatory_collapse_signature` refers to the exit behavior of bounded -(i) selection and should be evaluated by dominant_power_fraction with spectral_entropy as a secondary dispersion check when available.

### 6. Cross-Model Comparison
```json
{
  "correlation": 0.88,
  "agreement_type": "threshold_qualitative",
  "qualitative_match": ["Sharp threshold onset", "Broadband collapse signature"]
}
```

### 7. Falsification
- **Vector Name: FV-1 (Zero Mismatch):** Running the Structural Box with $s=0$ resulted in structural collapse (alignment rate $0.316$).
- **Vector Name: FV-2 (Natural Basin Control):** Kuramoto simulations exhibited a resonant ringdown ($0.51$ concentration), falsifying the claim that broadband bursts are universal to all collapse events.

### 8. Artifact Analysis
```json
{
  "seed_sensitivity": "Low (consistent across 3 seeds)",
  "parameter_sensitivity": "High (highly sensitive to kappa/lambda_R ratio)",
  "known_model_limits": ["1D spatial grid limitation", "Simplified coupling kernels"],
  "artifact_risk": "Low",
  "observable_separation": "Entry, persistence, and collapse terms are separated by lifecycle role; future runs should report persistence duration and spectral entropy explicitly."
}
```

### 9. Classification
**Proposed Interpretation (L2)**

*Capped at Proposed Interpretation because term-roles for `threshold_transition`, `stable_selection_regime`, and `non_oscillatory_collapse_signature` are currently below L3 in `registry/lexicon_validation_registry.json`.*

### 10. Conclusion
Within these models, biased transport remains a **proposed interpretation** of a threshold-dependent, meta-stable state of participating difference, with entry, persistence, and collapse behavior now separated into distinct lexicon-bound roles. The `non_oscillatory_collapse_signature` is a procedural consequence of collapse without dominant oscillatory relaxation under the tested forcing-removal protocol.

### 11. Next Steps
- Implement 2D C++ multi-model ensembles to characterize scaling.
- Higher-resolution TDA modules for realignment front mapping.

