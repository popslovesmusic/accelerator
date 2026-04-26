# Technical Paper — Law V (Admissibility) Empirical Probe

## 0. Metadata

```json
{
  "claim_id": "LAW_V_FILTER_RESIDUE_GATING_2026-04-25",
  "status": "L3",
  "classification": "Supported",
  "models_used": [
    "ca_admissibility_sim_v1",
    "fsa_rule_engine_sim_v1"
  ],
  "model_classes": [
    "CA",
    "FSA"
  ],
  "seeds_used": 3,
  "falsification_run": true,
  "overreach_check": "passed"
}
```

## 1. Abstract

We test **Law V.1 (“The Filter”)** from `theory/THE LAW OF THE ONE PROCESS.txt` as an operational claim: *in internally governed systems, “admissible continuation” is a strict subset of candidate continuation, and residue-like state acts as a gating variable that reduces admissibility as it accumulates*. We implement two independent model classes (a spatial CA admissibility process and a finite-state rule engine) and measure the fraction of admissible updates / continuing agents under systematically strengthened residue gating. We report cross-model agreement, correlation, and falsification outcomes.

## 2. Theoretical Mapping

```json
{
  "epsilon": "mismatch / local gradient signal that proposes continuation",
  "residue": "accumulated constraint / memory variable that gates continuation",
  "coupling": "reach / interaction domain: diffusion neighborhood (CA) or graph successor relation (FSA)"
}
```

## 3. Experimental Setup

- **CA (spatial admissibility):** `ca_admissibility_sim_v1/sim.py` with `grid_size=64`, `steps=500`, and a fixed central source.
  - Sweep levels in `outputs/research_residue_necessity_2026-04-25/configs/ca_sweep_L*.json`:
    - L0: `residue_growth=0.0`, `initial_residue=0.0`
    - L1: `residue_growth=0.01`, `initial_residue=0.05`
    - L2: `residue_growth=0.05`, `initial_residue=0.1`
    - L3: `residue_growth=0.1`, `initial_residue=0.2`
- **FSA (rule-engine admissibility):** `fsa_rule_engine_sim_v1/sim.py` with `n_agents=1000`, `steps=100`, `n_states=20`, `edge_prob=0.3`, `forbidden_node=0`, `residue_threshold_node=10`.
  - Seeds: `21, 22, 23` (graph + choice randomness).
  - Residue requirement sweep (`residue_required`) in `outputs/research_residue_necessity_2026-04-25/configs/fsa_sweep_*.json`:
    - L0: `0`, L1: `5`, L2: `15`, L3: `30`

All simulation outputs are under `outputs/research_residue_necessity_2026-04-25/runs/`.

## 4. Observables

```json
{
  "observable_1": "CA active_fraction = mean(admissible_mask) at final step",
  "observable_2": "FSA active_fraction = active_count / n_agents at final step, averaged over seeds",
  "normalization": "Both are already [0,1] fractions; no further scaling applied"
}
```

## 5. Results

Raw sweep endpoints (final-step activity):

- CA sweep (`runs/ca_sweep_L*/summary.json`):
  - L0: `active_fraction = 1.0`
  - L1: `active_fraction = 0.0068359375`
  - L2: `active_fraction = 0.006103515625`
  - L3: `active_fraction = 0.001953125`

- FSA sweep (mean over seeds 21/22/23; `runs/fsa_sweep_R*_seed*/summary.json`):
  - L0 (`residue_required=0`): `active_fraction_mean = 1.0`
  - L1 (`residue_required=5`): `active_fraction_mean = 0.588`
  - L2 (`residue_required=15`): `active_fraction_mean = 0.4013333333333333`
  - L3 (`residue_required=30`): `active_fraction_mean = 0.35033333333333333`

Derived sweep summary table is saved to `outputs/research_residue_necessity_2026-04-25/analysis/sweep_summary.csv`.

## 6. Cross-Model Comparison

```json
{
  "correlation": 0.9392453634189928,
  "agreement_type": "strong",
  "qualitative_match": [
    "Removing residue gating yields near-maximal continuation/activity (L0) in both models.",
    "Strengthening residue gating reduces continuation/activity (L1→L3) in both models."
  ]
}
```

The computed cross-model report is saved to `outputs/research_residue_necessity_2026-04-25/analysis/cross_model_comparison.json`.

## 7. Falsification

```json
{
  "tests_run": [
    "No Coupling -> No Synch (Kuramoto)",
    "Low Noise Trapping (Stochastic)",
    "Zero Mismatch -> Inert (CA)",
    "Admissibility Off (CA) -> Runaway Activity",
    "Strong Residue (CA) -> Low Activity",
    "Fully Gated (FSA) -> Immediate Halt",
    "No Gating + Dense Graph (FSA) -> All Active"
  ],
  "result": "PASS (7/7)",
  "notes": "Suite config: outputs/research_residue_necessity_2026-04-25/configs/falsification_suite_admissibility.json; report: outputs/research_residue_necessity_2026-04-25/runs/falsification/falsification_report.json"
}
```

## 8. Artifact Analysis

```json
{
  "seed_sensitivity": "CA admissibility engine is deterministic under the provided config (seed is present but not used by the engine). FSA shows high seed sensitivity due to random graph structure; some seeds preserve full activity even under higher residue_required.",
  "parameter_sensitivity": "CA activity fraction is highly sensitive to initial_residue and residue_growth; FSA activity is sensitive to residue_required, residue_threshold_node, and edge_prob (graph connectivity).",
  "known_model_limits": [
    "CA admissibility is defined as (local gradient > residue), which makes residue purely inhibitory under this implementation.",
    "FSA residue is a simple step counter; it is not a state-dependent physical memory signal, only a gating scalar.",
    "Neither model enforces or measures semantic 'structure preservation' beyond continued admissibility / non-halting."
  ]
}
```

## 9. Classification

- **Supported (L3)**: multi-model agreement (CA + FSA), ≥3 seeds (FSA seeds 21/22/23), and falsification suite executed and passed.

## 10. Conclusion

Within these models, **residue-like state functions as an internal admissibility gate**: reducing residue constraints increases the fraction of admissible updates / continuing agents, while strengthening residue gating reduces continuation/activity. The agreement is strong under the sweep mapping used here, and the limiting behaviors are supported by targeted falsification tests.

## 11. Next Steps

- Add a third model class cross-check (e.g., `graph_dynamics_sim_v1` or a stochastic threshold model) with an explicit residue-gated admissibility rule.
- For FSA, run additional seeds and vary `edge_prob` to quantify when residue gating primarily reduces activity vs. simply reorders reachable states.
- For CA, extend observables beyond activity fraction (e.g., spatial fragmentation/topology metrics via `tda_module_v1`) to connect “preserve structure” to measurable structure rather than only continuation rate.

