# T004: Hierarchical Stabilization (Nesting)

## 0. Metadata
```json
{
  "claim_id": "T004-NESTING-V1",
  "status": "L2",
  "classification": "supported",
  "charter_classification": "verified",
  "models_used": ["ca_admissibility_sim_v1_cpp"],
  "model_classes": ["discrete_ca"],
  "seeds_used": 1,
  "independent_measurement_count": 1,
  "falsification_run": true,
  "recoverable_outputs": ["results\2026-05-23_run09_Hierarchical_Nesting/"],
  "claim_gate_result": "pass"
}
```

## 1. Abstract
This report provides empirical evidence for **T004 (Hierarchical Stabilization)**. We demonstrate a "Recursive Basin Nesting" procedure where the output of a fine-grained process layer (Base) constrains the parameters of a coarse-grained layer (Top), leading to stable structures at both scales.

## 2. Results
- **Base Layer:** Active Fraction = 0.0139.
- **Top Layer (Coarse):** Active Fraction = 0.0481 (under scaled diffusion D=0.0070).
- **Scaling Symmetry:** Both layers successfully stabilized to non-zero persistence regimes.

## 3. Conclusion
Within these models, multiscale complexity emerges through the interaction web of lower-order regimes acting as the admissibility substrate for higher-order knots. This supports the "Law of Hierarchical Stabilization."
