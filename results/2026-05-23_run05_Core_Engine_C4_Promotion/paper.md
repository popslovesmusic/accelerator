# Core Engine C4 Promotion (Graph & CA)

## 0. Metadata
```json
{
  "claim_id": "CORE-ENGINE-C4-V1",
  "status": "L3",
  "classification": "supported",
  "charter_classification": "verified",
  "models_used": ["graph_dynamics_sim_v1_cpp", "ca_admissibility_sim_v1_cpp"],
  "model_classes": ["network", "discrete_ca"],
  "seeds_used": 3,
  "falsification_run": true,
  "recoverable_outputs": ["results/2026-05-23_run05_Core_Engine_C4_Promotion/"],
  "claim_gate_result": "pass"
}
```

## 1. Abstract
This report documents the C4 rigor endorsement of the core dynamics engines. Both `graph_dynamics_sim_v1_cpp` and `ca_admissibility_sim_v1_cpp` have passed stability, uncertainty, and falsification tests.

## 2. Results
- **Graph Dynamics:** Stable under seed variance; passed FV-2 (Boundary Collapse).
- **CA Admissibility:** Stable under diffusion variance; passed FV-1 (Zero Mismatch).

## 3. Conclusion
Within these models, the core engines are certified for C4 research claims.
