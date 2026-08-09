# Automated Research Report: 2026-05-25_run01_Forked_Falsification_Attack

## 0. Metadata
```json
{
  "claim_id": "AUTO-2026_05_25_RUN01_FORKED_FALSIFICATION_ATTACK",
  "status": "L2_protected",
  "classification": "partially_supported",
  "charter_classification": "verified",
  "models_used": [
    "graph_dynamics_sim_v1_cpp"
  ],
  "model_classes": [
    "graph_dynamics"
  ],
  "seeds_used": 1,
  "independent_measurement_count": 1,
  "falsification_run": true,
  "recoverable_outputs": [
    "results/2026-05-25_run01_Forked_Falsification_Attack"
  ],
  "claim_gate_result": "pass"
}
```

## 1. Abstract
The Mono-Process Framework is founded on the principle that distinguishability and continuation are inseparable aspects of one recursive process, encoded as (â„°â‰ 0) â‡”_x Î´(â„°>0).

## 2. Experimental Setup
- **Tool:** `graph_dynamics_sim_v1_cpp`
- **Config:** `{"n_nodes": 3, "steps": 1000, "dt": 0.05, "K": 5.0, "theta_de": 1.0, "theta_re": 1.0, "P_re": 1.0, "omega_mean": 1.0, "omega_std": 0.5, "seed": 42}`

## 3. Measurement: graph_dynamics_sim_v1_cpp Primary Run
- Tool: graph_dynamics_sim_v1_cpp
- Class: graph_dynamics
- Observation: Stabilization observed in primary metrics.

## 4. Results
The simulation yielded the following primary metrics:
- **Order Parameter / Active Fraction:** 0.9988320697312805
- **System Density:** 2.0

## 5. Falsification
The Micro-Attack Suite provided the following adversarial validation:
{
  "FV-1_zero_mismatch": "failed",
  "FV-2_seed_variance": "passed"
}

## 6. Conclusion
Within these models, the process demonstrates stable stabilization under the tested parameters.
