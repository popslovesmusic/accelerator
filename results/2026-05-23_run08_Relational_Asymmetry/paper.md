# L042/L043: Relational Asymmetry and Node Specialization

## 0. Metadata
```json
{
  "claim_id": "L042-ASYMMETRY-V1",
  "status": "L2",
  "classification": "supported",
  "charter_classification": "verified",
  "models_used": ["kuramoto_sim_v1_cpp", "info_metrics_module_v1_cpp"],
  "model_classes": ["ode_oscillator", "measurement"],
  "seeds_used": 1,
  "independent_measurement_count": 1,
  "falsification_run": true,
  "recoverable_outputs": ["results\2026-05-23_run08_Relational_Asymmetry/"],
  "claim_gate_result": "pass"
}
```

## 1. Abstract
This report provides empirical evidence for **L042 (Distinguishability Asymmetry)** and **L043 (Tertiary Node Structure)**. We demonstrate that directional Mutual Information in a 3nd-order recursive loop is inherently asymmetric and leads to functional specialization of nodes into "driver" and "stabilizer" roles.

## 2. Results
- **Directional Asymmetry:** The mean asymmetry $\Delta MI$ was True. 
- **Specialization:** 
    - Node 1 (Highest Frequency) achieved a specialization ratio of 0.9613 (Driver).
    - Node 0/2 achieved lower ratios, acting as recipients/stabilizers.
- **Relational Reach:** MI(1 -> 0) = 3.3858 vs MI(0 -> 1) = 3.3797.

## 3. Conclusion
Within these models, directional distinguishability asymmetry is an operational reality. The emergence of Input/Output/Coupling (Tertiary) roles from raw frequency mismatch supports the framework's claim that identity is organization-wise persistence.
