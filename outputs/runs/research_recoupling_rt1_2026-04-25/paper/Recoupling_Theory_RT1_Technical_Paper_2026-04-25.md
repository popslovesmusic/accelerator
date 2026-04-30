## 0. Metadata

```json
{
  "claim_id": "RT1_P1_admissibility_gating_2026-04-25",
  "status": "L3",
  "classification": "provisional",
  "models_used": [
    "ca_admissibility_sim_v1",
    "graph_dynamics_sim_v1",
    "rd_moving_boundary_sim_v1"
  ],
  "model_classes": [
    "CA",
    "Graph",
    "PDE"
  ],
  "seeds_used": 3,
  "falsification_run": true,
  "overreach_check": "passed"
}
```

## 1. Abstract

[PROVISIONAL] We operationalize RT-1 (“no realized mismatch without prior admissibility via a transition operator”) as an empirical invariant: **activation events must not occur in inadmissible regions**, and activation must be traceable to an admissible precursor within a finite time window. We test this across three model classes (CA, Graph, PDE) with three seeds per model where stochasticity is present. In CA and Graph implementations, inadmissible activation is exactly zero under the tested update rules; in the PDE moving-boundary implementation, activation at the admissibility boundary can occur while the local admissibility field is below threshold (soft channeling), producing a cross-model contradiction for RT-1 Prediction 1 as a model-class-general constraint. Evidence is recoverable in the program outputs cited below.

## 2. Theoretical Mapping

```json
{
  "epsilon": "mismatch signal (|epsilon| > epsilon_floor is treated as realized activity)",
  "residue": "local gate / constraint that sets an admissibility threshold for updates",
  "coupling": "interaction reach that constrains influence pathways (topology / corridor / adjacency)",
  "delta": "procedural transition operator that triggers admissible activation events"
}
```

## 3. Experimental Setup

- Source note: `theory/Recoupling Theory.txt`
- Program directory: `outputs/research_recoupling_rt1_2026-04-25`
- Wrapper runners (no engine modifications):
  - `outputs/research_recoupling_rt1_2026-04-25/wrappers/rt1_ca_runner.py`
  - `outputs/research_recoupling_rt1_2026-04-25/wrappers/rt1_graph_runner.py`
  - `outputs/research_recoupling_rt1_2026-04-25/wrappers/rt1_rd_runner.py`
- Baseline configs:
  - `outputs/research_recoupling_rt1_2026-04-25/configs/rt1_ca_baseline.json`
  - `outputs/research_recoupling_rt1_2026-04-25/configs/rt1_graph_baseline.json`
  - `outputs/research_recoupling_rt1_2026-04-25/configs/rt1_rd_baseline.json`
- Seeds: 101, 102, 103 (RD is deterministic under these configs but executed per-seed for protocol symmetry).
- Variants:
  - RD negative control intended to produce “signal outside domain”: `outputs/research_recoupling_rt1_2026-04-25/configs/rt1_rd_falsify_leak.json`

## 4. Observables

```json
{
  "observable_1": "inadmissible_activation_fraction_max (max_t [inadmissible_activation_events(t) / activation_events(t)])",
  "observable_2": "traceability_failure_fraction_max (max_t [untraceable_activation_events(t) / activation_events(t)])",
  "observable_3": "asymmetry_proxy (Graph: recouple_asymmetry_mean = mean_t[edge_added(t)/candidate_pairs(t)] ; CA: activation_fraction_of_admissible_mean ; RD: signal_outside_domain_fraction_max)",
  "normalization": "[0,1] fractions; correlations computed on seed-aligned per-run scalars where defined"
}
```

## 5. Results

Raw per-run scalar summaries are in `outputs/research_recoupling_rt1_2026-04-25/analysis/summary_table.csv`. (RT1 | summary_table | 2026-04-25 | outputs/research_recoupling_rt1_2026-04-25/analysis/summary_table.csv)

- CA baseline (seeds 101–103): `inadmissible_activation_fraction_max = 0.0`, `traceability_failure_fraction_max = 0.0`. (RT1 | ca_baseline | 2026-04-25 | outputs/research_recoupling_rt1_2026-04-25/runs/ca_baseline__seed101/summary.json)
- Graph baseline (seeds 101–103): `inadmissible_edge_add_fraction_max = 0.0`, `traceability_failure_fraction_max = 0.0`, `recouple_asymmetry_mean ≈ 0.018–0.020`. (RT1 | graph_baseline | 2026-04-25 | outputs/research_recoupling_rt1_2026-04-25/runs/graph_baseline__seed101/summary.json)
- RD baseline (seeds 101–103): `inadmissible_activation_fraction_max = 1.0`, `traceability_failure_fraction_max = 1.0`, `signal_outside_domain_fraction_max ≈ 0.0434`. (RT1 | rd_baseline | 2026-04-25 | outputs/research_recoupling_rt1_2026-04-25/runs/rd_baseline__seed101/summary.json)
- RD falsify_leak variant (seeds 101–103): `signal_outside_domain_fraction_max ≈ 0.194`. (RT1 | rd_falsify_leak | 2026-04-25 | outputs/research_recoupling_rt1_2026-04-25/runs/rd_falsify_leak__seed101/summary.json)

## 6. Cross-Model Comparison

```json
{
  "correlation": 0.0,
  "agreement_type": "partial",
  "qualitative_match": [
    "CA and Graph enforce inadmissible activation = 0 under their update rules.",
    "RD shows boundary-adjacent activation while D_before <= threshold, contradicting RT-1 P1 as a model-class-general constraint under the tested embedding."
  ]
}
```

Cross-model comparison artifact: `outputs/research_recoupling_rt1_2026-04-25/analysis/cross_model_comparison.json`. (RT1 | cross_model | 2026-04-25 | outputs/research_recoupling_rt1_2026-04-25/analysis/cross_model_comparison.json)

## 7. Falsification

```json
{
  "tests_run": [
    "RT1 P1: CA forbids inadmissible updates",
    "RT1 P1/P2: Graph forbids inadmissible recoupling",
    "RT1 Negative Control: RD can leak signal outside domain when decay is fast"
  ],
  "result": "PASS (3/3)",
  "notes": "Suite asserts strict gating in CA/Graph and demonstrates a constructive counterexample (signal outside domain) in RD under fast domain decay / high channel diffusion."
}
```

Falsification report: `outputs/research_recoupling_rt1_2026-04-25/runs/falsification/results/falsification_report.json`. (RT1 | falsification | 2026-04-25 | outputs/research_recoupling_rt1_2026-04-25/runs/falsification/results/falsification_report.json)

## 8. Artifact Analysis

```json
{
  "seed_sensitivity": "CA and Graph show seed-to-seed variability in asymmetry proxies but not in the gating invariants (inadmissible activation remained 0). RD results are deterministic under the baseline configs used here.",
  "parameter_sensitivity": "RD violations are sensitive to how admissibility is coupled to transport across boundaries (here: midpoint channeling allows boundary crossing even when the destination cell’s D_before <= threshold).",
  "known_model_limits": [
    "CA update rule enforces a hard gate by construction (inadmissible cells are never updated).",
    "Graph recoupling is gated by stress<threshold by construction; stress is computed before rewiring.",
    "RD uses a soft (midpoint) channeled diffusion operator which can introduce signal into cells that are locally below the admissibility threshold at the previous step."
  ]
}
```

## 9. Classification

- [PROVISIONAL] RT-1 Prediction 1 (“no activation without admissibility”) is **Partially Supported**: it holds in CA and Graph update rules but is contradicted in the tested PDE moving-boundary embedding. Therefore, RT-1 P1 is **Not Supported as a model-class-general constraint** under the present toolset.
- [PROVISIONAL] A narrower claim is supported: **within these models, strict ‘no activation outside admissibility’ behavior requires a hard gating implementation (or an explicit drain coupling outside admissible regions)**; soft boundary channeling can violate the invariant.

## 10. Conclusion

Within these models, admissibility-gated activation is operationally enforced in CA and Graph implementations, but the RD moving-boundary PDE embedding permits boundary-adjacent activations where local admissibility is below threshold (and allows nontrivial signal mass to persist outside the admissible domain). This contradicts RT-1 Prediction 1 as a universal constraint across model classes and indicates that the RT-1 PDE embedding would require a stricter admissibility-transport coupling (and/or an explicit drain term conditioned on inadmissibility) to match the “no spontaneous activation” requirement.

## 11. Next Steps

- Implement and test a *hard-gated* PDE transport variant (no signal transport across edges where destination admissibility is below threshold) as a separate RD engine version or configuration knob.
- Add event-level logging of admissibility predicates and activation events directly to the RD and Graph tools (or via standardized wrapper output) to reduce ambiguity in traceability definitions.
- Extend the cross-verification to a stochastic SDE onset model (`stochastic_sim_v1`) as an additional model class for activation-threshold behavior under noise floors.

