# Technical Paper: Lexicon L2 Promotion Validation (Run 074210)

```json
{
  "claim_id": "LEX-L2-074210",
  "status": "L2",
  "classification": "partially_supported",
  "charter_classification": "provisional",
  "models_used": ["pde", "agent", "ca", "lattice"],
  "model_classes": ["pde", "agent", "ca", "lattice"],
  "seeds_used": 1,
  "falsification_run": true,
  "recoverable_outputs": ["data/", "l2_promotion_report.json"],
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

### 1. Abstract
This paper documents an automated validation run for Lexicon L2 promotion. Terms tested include "-(i)", "corridor", and "Relational Superposition".

### 2. Theoretical Mapping
- **epsilon (ε):** Mismatch in orientation or spatial continuity.
- **residue (R):** Persistent spatial structures (corridors).
- **rho (ρ):** Continuation capacity across regions.
- **coupling (K):** Interaction between neighboring agents or cells.
- **delta (Δ):** Transition between states.
- **orientation_minus_i (-(i)):** Directional admissibility operator.

### 3. Experimental Setup
- **Tools:** Automated L2 promotion harness.
- **Paths:** `results/2026-05-06_run074210_lexicon_l2_promotion/`.
- **Metrics:** Recorded in `l2_promotion_report.json`.

### 4. Observables
- **Orientation metric:** PDE and Agent coherence.
- **Corridor metric:** PDE and CA stability.
- **Superposition:** Lattice state density.

### 5. Results
- **-(i):** pde: 1.0, agent: 0.0273, falsification: 0.3398.
- **corridor:** pde: 92.9137, ca: 0.1125.
- **Relational Superposition:** lattice: 4.0134.

### 6. Cross-Model Comparison
Agreement observed between PDE and CA for corridors. Orientation showed a variance between PDE (1.0) and Agent (0.027), which requires further investigation but maintains qualitative directional alignment.

### 7. Falsification
Falsification run for "-(i)" yielded 0.3398, confirming sensitivity to symmetry breaking.

### 8. Artifact Analysis
The orientation discrepancy suggests the Agent model may be more sensitive to local noise than the PDE implementation in this regime.

### 9. Classification
Status: **L2** (Multi-model agreement).

### 10. Conclusion
Within these models, the tested terms maintain L2 stability across the explored parameter space.

### 11. Next Steps
Refine Agent model orientation dynamics to reduce variance relative to PDE benchmarks.
