## 0. Metadata

```json
{
  "claim_id": "cdhds_dual_laws_invariant_test_2026-04-25",
  "status": "L3",
  "classification": "provisional",
  "models_used": [
    "rd_moving_boundary_sim_v1",
    "fsa_rule_engine_sim_v1",
    "graph_dynamics_sim_v1"
  ],
  "model_classes": [
    "PDE",
    "Discrete Automaton",
    "Graph Dynamics"
  ],
  "seeds_used": 3,
  "falsification_run": true,
  "overreach_check": "passed"
}
```

## 1. Abstract

[PROVISIONAL] Using two primary source notes, we derive a falsifiable CDHDS-style enforcement hypothesis for the frame statement `(ℰ≠0) ⇔ δ(ℰ>0)`: **(i)** updates/recouplings must originate from admissible precursors (no forbidden-origin change), **(ii)** updates must land back in an admissible set, and **(iii)** continuous flow may not persist in a forbidden region without a timely recoupling event. We test these invariants across three model classes (PDE moving boundary, discrete rule engine, dynamic graph). The results contradict cross-model invariance under the current toolset: hard-gated discrete/graph models satisfy the invariants by construction for the tested roles, while the PDE moving-boundary embedding exhibits persistent “outside-domain signal” and outside-activation events that do not recouple within the configured window. All empirical statements are backed by recoverable outputs cited below.

Primary sources:
- `theory/master/research_dual_laws_v1/formal_treatment_cdhds.md`
- `theory/master/note.txt`

## 2. Theoretical Mapping

```json
{
  "epsilon": "ε: mismatch / nonzero participation signal (operationally: S>epsilon_floor or stress<threshold or state!=forbidden)",
  "residue": "R: history accumulator that gates future admissibility (explicit in FSA; implicit/absent in Graph/RD tests here)",
  "coupling": "K: interaction kernel / reachability constraint (topology A in Graph; channeled transport via D in RD)",
  "delta": "δ: transition/update operator (domain recoupling events in RD; state transitions in FSA; edge additions in Graph)"
}
```

## 3. Experimental Setup

Program directory: `outputs/research_dual_laws_cdhds_v1_2026-04-25`

Wrappers (no engine modifications):
- `outputs/research_dual_laws_cdhds_v1_2026-04-25/wrappers/cdhds_rd_runner.py`
- `outputs/research_dual_laws_cdhds_v1_2026-04-25/wrappers/cdhds_fsa_runner.py`
- `outputs/research_dual_laws_cdhds_v1_2026-04-25/wrappers/cdhds_graph_runner.py`

Configs:
- RD baseline: `outputs/research_dual_laws_cdhds_v1_2026-04-25/configs/cdhds_rd_baseline.json`
- RD negative control (intended violation): `outputs/research_dual_laws_cdhds_v1_2026-04-25/configs/cdhds_rd_negative_no_recouple.json`
- FSA baseline: `outputs/research_dual_laws_cdhds_v1_2026-04-25/configs/cdhds_fsa_baseline.json`
- Graph baseline: `outputs/research_dual_laws_cdhds_v1_2026-04-25/configs/cdhds_graph_baseline.json`

Seeds: 101, 102, 103 (RD is deterministic under these baseline configs; repeats are retained to meet the protocol requirement and to make deterministic behavior explicit.)

## 4. Observables

```json
{
  "observable_1": "RD outside-activation non-recouple fraction: outside_activation_no_recouple_fraction_max",
  "observable_2": "Graph inadmissible recouple fraction: inadmissible_edge_add_fraction_max",
  "observable_3": "FSA terminality indicator: active_without_admissible_continuation_total",
  "normalization": "Fractions are in [0,1]; event totals are reported as counts."
}
```

Operational definitions (by model):
- RD admissible set A: cells with `D > domain_admissibility_thresh`; forbidden set F: `D <= thresh`. δ-event: a cell’s `D` crossing forbidden→admissible (recoupling).
- Graph admissible continuation set: candidate pairs with `stress < recouple_threshold`; δ-event: edge addition.
- FSA admissible continuation set: `engine.get_admissible_continuations(state, residue)`; forbidden state: node 0; δ-event: state transition.

## 5. Results

Per-run scalar summary table: `outputs/research_dual_laws_cdhds_v1_2026-04-25/analysis/summary_table.csv`. (CDHDS | summary_table | 2026-04-25 | outputs/research_dual_laws_cdhds_v1_2026-04-25/analysis/summary_table.csv)

### 5.1 Graph (Topology Layer)

- Baseline: `inadmissible_edge_add_fraction_max = 0.0` for seeds 101–103. (CDHDS | graph_baseline | 2026-04-25 | outputs/research_dual_laws_cdhds_v1_2026-04-25/runs/graph_baseline__seed101/summary.json)

Interpretation (scoped): Within this graph engine, recoupling additions are admissibility-gated by the stress threshold by construction; this supports the “no forbidden-origin recoupling” invariant for this operational role.

### 5.2 FSA (Discrete/Event Layer)

- Forbidden occupancy: `forbidden_occupancy_events_total = 0` and `transitions_to_forbidden_total = 0` for seeds 101–103. (CDHDS | fsa_baseline | 2026-04-25 | outputs/research_dual_laws_cdhds_v1_2026-04-25/runs/fsa_baseline__seed101/summary.json)
- Terminality / “no mapping exists” events: `active_without_admissible_continuation_total = 686` for seed 103 (0 for seeds 101–102). (CDHDS | fsa_baseline | 2026-04-25 | outputs/research_dual_laws_cdhds_v1_2026-04-25/runs/fsa_baseline__seed103/summary.json)

Interpretation (scoped): The L0-style forbidden state exclusion holds in this discrete model, but the stronger “admissible element ⇔ mapping exists” condition fails under some random graph realizations because dead ends occur (agents become active at a state with no admissible continuation).

### 5.3 RD Moving Boundary (Continuous Layer)

- Baseline: `outside_activation_no_recouple_fraction_max ≈ 0.941` (seeds 101–103 identical under deterministic baseline). (CDHDS | rd_baseline | 2026-04-25 | outputs/research_dual_laws_cdhds_v1_2026-04-25/runs/rd_baseline__seed101/summary.json)
- Baseline: nonzero but small persistent signal mass outside admissible domain: `signal_outside_domain_fraction_max ≈ 0.0434`. (CDHDS | rd_baseline | 2026-04-25 | outputs/research_dual_laws_cdhds_v1_2026-04-25/runs/rd_baseline__seed101/summary.json)

Interpretation (scoped): Under this embedding, signal transport can activate cells outside the admissible domain faster than the domain recouples them, producing persistent outside-domain activity and violating the “no continuous flow persists in F without timely δ recoupling” constraint as operationalized here.

## 6. Cross-Model Comparison

```json
{
  "agreement_type": "contradiction",
  "qualitative_match": [
    "Graph and (parts of) FSA satisfy gating invariants by construction for their tested roles.",
    "RD violates the analogous invariant under the tested admissibility/recoupling coupling."
  ]
}
```

Artifact: `outputs/research_dual_laws_cdhds_v1_2026-04-25/analysis/cross_model_comparison.json`. (CDHDS | cross_model | 2026-04-25 | outputs/research_dual_laws_cdhds_v1_2026-04-25/analysis/cross_model_comparison.json)

## 7. Falsification

```json
{
  "tests_run": [
    "CDHDS FSA: forbidden state never occupied",
    "CDHDS Graph: recoupling only from admissible candidate set",
    "CDHDS RD Negative Control: outside activation fails to recouple within window"
  ],
  "result": "PASS (3/3)",
  "notes": "Negative control demonstrates the RD invariant test can detect non-recoupling outside activations under parameter settings intended to block recoupling."
}
```

Report: `outputs/research_dual_laws_cdhds_v1_2026-04-25/runs/falsification/results/falsification_report.json`. (CDHDS | falsification | 2026-04-25 | outputs/research_dual_laws_cdhds_v1_2026-04-25/runs/falsification/results/falsification_report.json)

## 8. Artifact Analysis

```json
{
  "seed_sensitivity": "RD baseline is deterministic under current baseline config; Graph shows small seed-dependent variation in recouple_asymmetry_mean; FSA shows seed-dependent occurrence of dead ends (terminal states).",
  "parameter_sensitivity": "RD results are sensitive to (S_diff, beta, growth_thresh, domain_decay) which jointly determine whether domain recoupling keeps pace with signal transport.",
  "known_model_limits": [
    "Graph and FSA implement hard admissibility gates; success on gating invariants may be tautological for those roles.",
    "RD uses a continuous channeling operator that can transport signal across a boundary faster than the domain recouples; this may reflect embedding mismatch rather than a failure of the abstract frame itself.",
    "The mapping of (ℰ≠0) and δ is model-specific; alternative operationalizations may yield different outcomes."
  ]
}
```

## 9. Classification

- This study achieves **L3 experimental rigor** (≥2 model classes, ≥3 seeds, cross-model comparison, falsification run).
- The **frame-level invariants are Not Supported as cross-model universal constraints** under the present toolset and operationalizations, because the RD embedding contradicts the gating/recoupling requirement and the FSA model exhibits terminal dead ends for some random realizations.
- All empirical statements in this paper remain **[PROVISIONAL]** in the charter sense because the outputs are not produced under the charter v2.3 annex_B metric schema.

## 10. Conclusion

Within these models, the dual-law frame `(ℰ≠0) ⇔ δ(ℰ>0)` can be satisfied as an enforced constraint in hard-gated discrete/topological engines, but it does not emerge as an invariant across model classes under a soft moving-boundary PDE embedding and random discrete graph realizations. This indicates that “dual-law” behavior is, at minimum, **implementation-dependent**: cross-model invariance would require either (i) stricter transport gating / projection back into A in the continuous embedding, and/or (ii) explicit dead-end elimination / repair rules in the discrete engine to prevent terminal states.

## 11. Next Steps

- RD: add (or simulate via a wrapper/modified engine version) a hard constraint that prevents signal transport into cells with `D <= thresh` unless `D` recouples in the same step; then rerun to test whether the contradiction is an embedding artifact.
- FSA: enforce a “no dead ends” graph construction constraint (or add a repair transition rule) and rerun to test the L1 “no terminal state” law operationally.
- Add a fourth model class (e.g., `agent_based_sim_v1`) with an explicit admissibility boundary and discrete δ-hand-off to test the CDHDS event architecture more directly.

