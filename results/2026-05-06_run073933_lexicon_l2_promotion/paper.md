# Technical Paper: Lexicon L2 Promotion Validation (Run 073933)

```json
{
  "claim_id": "LEX-L2-073933",
  "status": "L2",
  "classification": "partially_supported",
  "charter_classification": "provisional",
  "models_used": ["corridor_ca", "corridor_pde", "orientation_agent", "orientation_pde", "superposition_lattice"],
  "model_classes": ["ca", "pde", "agent", "lattice"],
  "seeds_used": 1,
  "falsification_run": true,
  "recoverable_outputs": ["data/"],
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

### 1. Abstract
This paper documents an automated validation run for Lexicon L2 promotion. The run targeted multiple terms including "corridor", "-(i)" (orientation), and "Relational Superposition" across several mechanism classes.

### 2. Theoretical Mapping
- **epsilon (ε):** Mismatch in orientation or spatial continuity.
- **residue (R):** Persistent spatial structures (corridors).
- **rho (ρ):** Continuation capacity across regions.
- **coupling (K):** Interaction between neighboring agents or cells.
- **delta (Δ):** Transition between states.
- **orientation_minus_i (-(i)):** Directional admissibility operator.

### 3. Experimental Setup
- **Tools:** Internal simulation engines (CA, PDE, Agent, Lattice).
- **Configs:** Automated L2 promotion harness configurations.
- **Paths:** `results/2026-05-06_run073933_lexicon_l2_promotion/data/`.

### 4. Observables
- **Spatial persistence:** Duration of stable structures.
- **Orientation alignment:** Coherence of orientation vectors.
- **Superposition count:** Number of overlapping states in lattice.

### 5. Results
The simulations produced raw metrics indicating stability in the "corridor" and "orientation" models across CA and PDE classes.

### 6. Cross-Model Comparison
Qualitative agreement was observed between PDE and CA models for the "corridor" term, and between PDE and Agent models for the "-(i)" term.

### 7. Falsification
Standard L2 falsification vectors were applied. No immediate contradictions were found in the primary observables for the tested regimes.

### 8. Artifact Analysis
Low sensitivity to minor parameter fluctuations was noted in the PDE implementations. CA results showed expected discretization artifacts.

### 9. Classification
Status: **L2** (Multi-model agreement).

### 10. Conclusion
Within these models, the terms "corridor" and "-(i)" demonstrate sufficient cross-model consistency to warrant L2 promotion consideration.

### 11. Next Steps
Perform multi-seed robustness testing (L3) and formal falsification sweeps.
