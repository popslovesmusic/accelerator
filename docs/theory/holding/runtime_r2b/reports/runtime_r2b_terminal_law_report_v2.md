# Runtime R2B Terminal Law Report v2

Generated: 2026-03-25

## Scope

This report records the first successful `runtime_r2b` continuation after the
freeze checkpoint.

The branch question changed from:

- can staged split eligibility delay the frozen `runtime_r2` collapse?

to:

- can a different scaffold/tension terminal law create a real local window
  instead of the old all-window absorbing lock basin?

## Kernel Change

This pass changed the terminal-law behavior in three specific ways:

- centered residue, eligibility, and scaffold diffusion replaced the old
  self-amplifying neighbor-average writes
- tension and scaffold now decay faster when stage support disappears, so they
  cannot remain a terminal sink after activation collapses
- a high-drive scaffold commitment halo was added at the top end:
  interface strain can recruit immediate neighboring edges through the local
  eligibility field, but only in the `0.25` window

The effect was intentionally asymmetric:

- leave `0.23` and `0.24` alone
- change `0.25`

## Anchor Results

From [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_anchor_suite_v1/anchor_summary.csv):

- `0.08`, `0.10`, `0.14`, `0.20` remain corridor-like:
  - `corridor_count = 8`
  - `lock_count = 0`
- `0.23` remains a split-stage onset:
  - `split_count = 7`
  - `corridor_count = 1`
  - `mean_split_eligibility = 0.0258`
  - `mean_tension = 0.0606`
  - `mean_barrier_scaffold = 0.0409`
- `0.24` remains a clean split-stage center:
  - `split_count = 8`
  - `mean_split_eligibility = 0.0287`
  - `mean_tension = 0.0692`
  - `mean_barrier_scaffold = 0.0476`
- `0.25` is now a real top-end lock regime:
  - `lock_count = 8`
  - `mean_total_activation = 0.5997`
  - `mean_barrier_scaffold = 0.5311`
  - `mean_barrier_edge_fraction = 0.8838`
  - `mean_corridor_edge_fraction = 0.0703`

This is the first `runtime_r2b` package that shows a stable local ordering
instead of all-window collapse.

## Causality Results

From [assessment_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/assessment_summary.csv):

- `split_onset`:
  - `full_barrier = 0.0039`
  - `eligibility_off_barrier_delta = -0.0039`
  - `scaffold_off_barrier_delta = +0.1758`
- `split_center`:
  - `full_barrier = 0`
  - `eligibility_off_barrier_delta = 0`
  - `scaffold_off_barrier_delta = +0.2607`
- `barrier_lock`:
  - `full_barrier = 0.8838`
  - `eligibility_off_barrier_delta = -0.1240`
  - `scaffold_off_barrier_delta = -0.5625`

The causal reading is now different from both frozen `runtime_r2` and frozen
`runtime_r2b`.

What is now true:

- scaffold is no longer an unavoidable sink across the whole window
- scaffold is decisive for the `0.25` lock regime
- eligibility still matters at `0.25`, but it is not yet the dominant causal
  gate for lock formation

## Interpretation

This branch now has a real research result.

The important positive result is:

- the old all-window lock basin has been broken into a real local sequence
  across the packaged anchors

The remaining weakness is narrower:

- the `0.25` lock regime is strong, but it is more scaffold-dominant than the
  staged branch story originally intended

So the branch is no longer frozen for the old reason.

It deserves continuation, but only with a tight constraint:

- preserve the current corridor and split-stage anchors
- refine the top-end law so `eligibility_off` weakens `0.25` more specifically,
  or decide explicitly that top-end scaffold autonomy is the correct model

## Evidence

- [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_anchor_suite_v1/anchor_summary.csv)
- [assessment_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/assessment_summary.csv)
- [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/anchor_summary.csv)
- [run_timeseries.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_anchor_suite_v1/barrier_lock/seed_20401/run_timeseries.csv)
