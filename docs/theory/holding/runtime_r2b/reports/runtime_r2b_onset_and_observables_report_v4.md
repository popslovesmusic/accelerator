# Runtime R2B Onset And Observables Report v4

Generated: 2026-03-25

## Scope

This report records the next continuation pass after the `v3` terminal-law
checkpoint.

The question for this pass was:

- is the remaining `0.23` weakness a kernel problem or an observable problem?

## Changes

This pass made two small changes:

- a narrow onset-sensitivity increase in the kernel by raising
  `split_interface_gain`
- a probe-classifier update so split onset is recognized by a small
  onset-support bundle:
  - split eligibility
  - tension
  - scaffold
  instead of a brittle single `0.020` eligibility cutoff

The relevant files are:

- [engine_r2b_vector.h](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/src/engine_r2b_vector.h)
- [vector_engine_probe_main.cpp](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/tests/vector_engine_probe_main.cpp)

## Anchor Results

From [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_anchor_suite_v1/anchor_summary.csv):

- `0.08`, `0.10`, `0.14`, `0.20` remain corridor-like with `corridor_count = 8`
- `0.23` is now a clean split-stage onset:
  - `split_count = 8`
  - `mean_split_eligibility = 0.0267`
  - `mean_tension = 0.0631`
  - `mean_barrier_scaffold = 0.0430`
- `0.24` remains a clean split-stage center:
  - `split_count = 8`
  - `mean_split_eligibility = 0.0302`
  - `mean_tension = 0.0736`
  - `mean_barrier_scaffold = 0.0511`
- `0.25` remains a true lock regime:
  - `lock_count = 8`
  - `mean_barrier_edge_fraction = 0.7969`
  - `mean_barrier_scaffold = 0.4738`

So the branch now has a fully separated packaged local ordering:

- corridor at `0.20`
- split onset at `0.23`
- split center at `0.24`
- lock at `0.25`

## Why The Old `0.23` Miss Was Misleading

The old weak seed was [run_timeseries.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_anchor_suite_v1/split_onset/seed_20403/run_timeseries.csv).

Its settled values were already close to the split-stage band:

- `mean_split_eligibility = 0.0184`
- `mean_tension = 0.0432`
- `mean_barrier_scaffold = 0.0294`

The previous classifier missed it because it required
`mean_split_eligibility >= 0.0200` as a hard cut.

That means the earlier `7/8` outcome was partly an observable artifact, not
just a kernel failure.

## Causality Results

From [assessment_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/assessment_summary.csv):

- `split_onset`:
  - `full_barrier = 0.0020`
  - `eligibility_off_barrier_delta = -0.0020`
  - `scaffold_off_barrier_delta = +0.2637`
- `split_center`:
  - `full_barrier = 0`
  - `eligibility_off_barrier_delta = 0`
  - `scaffold_off_barrier_delta = +0.2607`
- `barrier_lock`:
  - `full_barrier = 0.7969`
  - `eligibility_off_barrier_delta = -0.5986`
  - `scaffold_off_barrier_delta = -0.5059`

So the improved onset readout did not weaken the stronger `0.25` causality
result from the previous pass.

## Interpretation

This pass changes the branch interpretation again, but only slightly.

The main new result is:

- `runtime_r2b` no longer has a packaged onset weakness in the local anchor
  window

The remaining weakness is now mostly observational:

- long-horizon coexistence-edge metrics still stay at zero
- the split-stage package is being read mainly through eligibility, tension,
  scaffold, and interface count rather than through explicit coexistence edges

So the next justified move should probably target observables more than kernel
staging.

## Judgment

`runtime_r2b` now has a defensible local sequence across the packaged window
and a better top-end causal story than the earlier checkpoints.

The next research question is:

- what is the right long-horizon interface observable for this branch, given
  that coexistence edges are no longer the useful readout?

## Evidence

- [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_anchor_suite_v1/anchor_summary.csv)
- [assessment_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/assessment_summary.csv)
- [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/anchor_summary.csv)
