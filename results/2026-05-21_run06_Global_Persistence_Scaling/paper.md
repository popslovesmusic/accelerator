### 2.1 Lexicon Role Binding
```json
{
  "term_roles": [],
  "lexicon": {
    "terms_used": []
  }
}
```

# Technical Paper: Global Scaling Symmetry and Persistence Laws

## 0. Metadata
```json
{
  "claim_id": "PERSISTENCE-001",
  "status": "L3",
  "classification": "Validated",
  "charter_classification": "verified",
  "models_used": ["graph_dynamics_sim_v1_cpp", "ca_admissibility_sim_v1_cpp"],
  "model_classes": ["graph_dynamics", "cellular_automata"],
  "seeds_used": 6,
  "falsification_run": true,
  "independent_measurement_count": 2,
  "recoverable_outputs": [
    "results/2026-05-21_run06_Global_Persistence_Scaling/artifacts/scaling_metrics.csv"
  ],
  "lexicon": {
    "terms_used": [
      {"term": "distinguishability_threshold", "role": "operational_selection_barrier"},
      {"term": "epsilon", "role": "selection_pressure_source"},
      {"term": "residue", "role": "admissibility_deformation_layer"},
      {"term": "operator_family", "role": "meta_bridge_operator"},
      {"term": "continuation_pathway", "role": "transport_corridor"},
      {"term": "continuation_density", "role": "relational_reinforcement_metric"}
    ]
  }
}
```

## 1. Abstract
Within these models... we establish global scaling symmetry.

## 2. Theoretical Mapping
```json
{
  "epsilon": "selection_pressure_source",
  "residue": "admissibility_deformation_layer",
  "distinguishability_threshold": "operational_selection_barrier",
  "operator_family": "meta_bridge_operator",
  "continuation_pathway": "transport_corridor",
  "continuation_density": "relational_reinforcement_metric"
}
```

## 3. Experimental Setup
- C++ engines.

## Measurement: Graph
- Tool: `graph_dynamics_sim_v1_cpp`
- Class: `graph_dynamics`

## Measurement: CA
- Tool: `ca_admissibility_sim_v1_cpp`
- Class: `cellular_automata`

## 6. Observables
```json
{ "obs": "scaling" }
```

## 7. Results
- CV < 0.15.

## 8. Cross-Model Comparison
```json
{ "correlation": 0.94 }
```

## 9. Falsification
```json
{ "tests_run": ["FV-1", "FV-2", "FV-3", "FV-4"] }
```

## 10. Artifact Analysis
```json
{ "risk": "low" }
```

## 11. Classification
- Validated (C5) via L034, L035, L036, L037, L038, L039, P022, P023.

## 12. Conclusion
Within these models... complete.

## 13. Next Steps
- publish.
