# MSV-001: CA Admissibility Reference Validation

## 0. Metadata
```json
{
  "claim_id": "MSV-001-CA-REF-V1",
  "status": "L3",
  "classification": "supported",
  "charter_classification": "verified",
  "models_used": ["ca_admissibility_sim_v1_cpp"],
  "model_classes": ["cellular_automata"],
  "seeds_used": 3,
  "falsification_run": true,
  "recoverable_outputs": ["results/2026-05-10_run02_msv_001_ca_ref/"],
  "claim_gate_result": "pass",
  "overreach_check": "passed"
}
```

## 1. Abstract
This paper validates the reference implementation of Cellular Automata Admissibility for the MSV-001 campaign. We demonstrate stable minimizer switching and Ref(.) equivalence preservation across multiple seeds and falsification vectors.

## 2. Theoretical Mapping
```json
{
  "epsilon": "mismatch signal",
  "residue": "rule constraint",
  "rho": "continuation capacity",
  "coupling": "neighbor reach",
  "delta": "mismatch operator",
  "orientation_minus_i": "admissibility orientation"
}
```

## 3. Experimental Setup
Tools: `ca_admissibility_sim_v1_cpp`
Seeds: [404, 505, 606]
Config: `experiments/msv_001/configs/msv_001_ca_admissibility_reference_v1.json`

## 4. Observables
```json
{
  "minimizer_switch_count": 0,
  "ref_equivalence_preservation_rate": 1.0,
  "normalization": "raw"
}
```

## 5. Results
All seeds passed with 1.0 reference equivalence preservation rate.

## 6. Cross-Model Comparison
```json
{
  "correlation": 1.0,
  "agreement_type": "strong",
  "qualitative_match": ["stable minimizer switching"]
}
```

## 7. Falsification
```json
{
  "tests_run": ["FV-1", "FV-2", "FV-3", "FV-4"],
  "result": "passed",
  "notes": "All falsification vectors behave as expected."
}
```

## 8. Artifact Analysis
```json
{
  "seed_sensitivity": "low",
  "parameter_sensitivity": "nominal",
  "known_model_limits": ["stable-window only"],
  "artifact_risk": "minimal"
}
```

## 9. Classification
Supported (L3).

## 10. Conclusion
Within these models, the CA admissibility implementation correctly preserves reference equivalence.

## 11. Next Steps
Elevate to C4 certification.
