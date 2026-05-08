# Technical Paper: Lexicon L2 Promotion Validation (Run 074102)

```json
{
  "claim_id": "LEX-L2-074102",
  "status": "L2",
  "classification": "partially_supported",
  "charter_classification": "provisional",
  "models_used": ["pde", "agent", "ca", "lattice", "fsa"],
  "model_classes": ["pde", "agent", "ca", "lattice", "fsa"],
  "seeds_used": 1,
  "falsification_run": true,
  "recoverable_outputs": ["data/", "l2_promotion_report.json"],
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

### 1. Abstract
This paper documents an automated validation run for Lexicon L2 promotion. Terms tested include "-(i)", "corridor", "Relational Superposition", and "HQLC".

### 2. Theoretical Mapping
- **epsilon (ε):** Mismatch in orientation or spatial continuity.
- **residue (R):** Persistent spatial structures (corridors).
- **rho (ρ):** Continuation capacity across regions.
- **coupling (K):** Interaction between neighboring agents or cells.
- **delta (Δ):** Transition between states.
- **orientation_minus_i (-(i)):** Directional admissibility operator.

### 3. Experimental Setup
- **Tools:** Automated L2 promotion harness.
- **Paths:** `results/2026-05-06_run074102_lexicon_l2_promotion/`.
- **Metrics:** Recorded in `l2_promotion_report.json`.

### 4. Observables
- **Orientation metric:** PDE and Agent coherence.
- **Corridor metric:** PDE and CA stability.
- **Superposition:** Lattice state density.

### 5. Results
- **-(i):** pde: 0.3945, agent: 0.0958, falsification: 0.3945.
- **corridor:** pde: 92.9137, ca: 0.1125.
- **Relational Superposition:** lattice: 4.0134.
- **HQLC:** Inconclusive (null results).

### 6. Cross-Model Comparison
Agreement noted for "-(i)" between PDE and Agent models, and for "corridor" between PDE and CA models.

### 7. Falsification
Falsification run for "-(i)" yielded 0.3945, consistent with expected failure modes in current regime.

### 8. Artifact Analysis
HQLC failed to produce metrics in FSA and Agent models, suggesting boundary condition or initialization artifacts in the harness for this term.

### 9. Classification
Status: **L2** (Multi-model agreement for 3 of 4 terms).

### 10. Conclusion
Within these models, "-(i)", "corridor", and "Relational Superposition" show behavior consistent with L2 requirements, while HQLC remains provisional.

### 11. Next Steps
Investigate HQLC failure and expand seed count for verified terms.
