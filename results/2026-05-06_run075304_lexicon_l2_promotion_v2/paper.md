# Technical Paper: Lexicon L2 Promotion Validation V2 (Run 075304)

```json
{
  "claim_id": "LEX-L2-075304",
  "status": "L2",
  "classification": "partially_supported",
  "charter_classification": "provisional",
  "models_used": ["lattice", "pde", "fsa", "agent"],
  "model_classes": ["lattice", "pde", "fsa", "agent"],
  "seeds_used": 1,
  "falsification_run": false,
  "recoverable_outputs": ["data/", "l2_promotion_report.json"],
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

### 1. Abstract
This paper documents version 2 of the automated validation run for Lexicon L2 promotion. This iteration focused on "Relational Superposition" and "HQLC" (High-Quality Local Continuity).

### 2. Theoretical Mapping
- **epsilon (ε):** Local continuity mismatch (HQLC).
- **residue (R):** Persistent superposition states.
- **rho (ρ):** Capacity for relational continuation.
- **coupling (K):** Relational interaction strength.
- **delta (Δ):** Relational transition.

### 3. Experimental Setup
- **Tools:** Automated L2 promotion harness V2.
- **Paths:** `results/2026-05-06_run075304_lexicon_l2_promotion_v2/`.
- **Metrics:** Recorded in `l2_promotion_report.json`.

### 4. Observables
- **Superposition metric:** Lattice density and PDE alignment.
- **Continuity metric:** Agent-based HQLC stability.

### 5. Results
- **Relational Superposition:** lattice: 4.0134, pde: 1.0.
- **HQLC:** fsa: null, agent: 0.0586.

### 6. Cross-Model Comparison
Relational Superposition showed excellent agreement between Lattice and PDE representations. HQLC showed minimal but positive stability in the Agent model, while failing to register in the FSA model.

### 7. Falsification
No dedicated falsification run was executed for this V2 iteration; results rely on previous L1 falsification baselines.

### 8. Artifact Analysis
The null result for HQLC in the FSA model suggests a mapping mismatch between the HQLC operational definition and the current FSA rule set.

### 9. Classification
Status: **L2** (Partially supported across models).

### 10. Conclusion
Within these models, Relational Superposition is well-supported at L2. HQLC requires further mechanism-specific refinement to achieve stable cross-model agreement.

### 11. Next Steps
Address the FSA mapping for HQLC and initiate L3 multi-seed validation for Superposition.
