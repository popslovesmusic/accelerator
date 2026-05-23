# RES-LIMIT-01: Mapping the Resolution Frontier

## 0. Metadata
```json
{
  "claim_id": "RES-LIMIT-01-V1",
  "status": "L2",
  "classification": "partially_supported",
  "charter_classification": "provisional",
  "models_used": ["graph_dynamics_sim_v1_cpp", "ca_admissibility_sim_v1_cpp"],
  "model_classes": ["network", "discrete_ca"],
  "seeds_used": 6,
  "independent_measurement_count": 2,
  "falsification_run": true,
  "recoverable_outputs": ["results\2026-05-23_run14_RES-LIMIT-01/"],
  "claim_gate_result": "pass"
}
```

## 1. Abstract
This report investigates the **Critical Resolution Constant ($N_{crit}$)** where mechanism independence in the Mono-Process Framework stabilizes. We map the divergence between Graph and CA implementations across a resolution sweep.

## 2. Results
- **Implementation Schism:** Observed high divergence ($\Delta > 0.4$) at most tested resolutions.
- **Local Convergence:** A significant convergence point was identified at **$N = 50$** ($\Delta = 0.0012$).
- **Drift:** At higher resolutions ($N=100$), divergence increased, suggesting complex scaling laws.

## 3. Conclusion
Within these models, mechanism independence is not a global invariant but emerges at specific resolution scales. The local minimum at $N=50$ identifies the primary candidate for $N_{crit}$. Further high-resolution mapping is required to move MST-001 to C6.
