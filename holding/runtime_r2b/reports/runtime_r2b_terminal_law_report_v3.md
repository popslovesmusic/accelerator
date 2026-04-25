# Runtime R2B Terminal Law Report v3

Generated: 2026-03-25

## Scope

This report records the second post-freeze `runtime_r2b` continuation pass.

The specific target for this pass was not stronger lock in general. It was:

- preserve the recovered `0.23` and `0.24` split window
- keep `0.25` as a real lock regime
- make the `0.25` lock more specifically eligibility-mediated

## Kernel Change

Relative to the previous terminal-law checkpoint, this pass changed only the
top-end causality path:

- the `0.25` commitment zone now weights interface strain by the local
  eligibility halo instead of letting raw strain dominate by itself
- scaffold-fed tension is now gated by eligibility support, so scaffold cannot
  rebuild the whole loop as easily when eligibility is absent
- the top-end commitment gain was raised to recover full-anchor lock strength
  after tightening the causal gate

The relevant kernel files are:

- [engine_r2b_vector.h](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/src/engine_r2b_vector.h)
- [engine_r2b_vector.cpp](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/src/engine_r2b_vector.cpp)

## Anchor Results

From [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_anchor_suite_v1/anchor_summary.csv):

- `0.08`, `0.10`, `0.14`, `0.20` remain corridor-like with `corridor_count = 8`
- `0.23` remains a split-stage onset with `split_count = 7`, `corridor_count = 1`
- `0.24` remains a clean split-stage center with `split_count = 8`
- `0.25` remains a true lock regime with:
  - `lock_count = 8`
  - `mean_barrier_scaffold = 0.4429`
  - `mean_barrier_edge_fraction = 0.7334`
  - `mean_corridor_edge_fraction = 0.1865`
  - `mean_split_eligibility = 0.0074`

So the recovered local ordering survived the causality refinement:

- corridor at `0.20`
- split at `0.23` and `0.24`
- lock at `0.25`

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
  - `full_barrier = 0.7334`
  - `eligibility_off_barrier_delta = -0.5352`
  - `scaffold_off_barrier_delta = -0.4121`

The important change is at `0.25`.

In this version:

- `full` is still a lock candidate
- `eligibility_off` is no longer a lock candidate
- `scaffold_off` is also not a lock candidate
- the larger barrier reduction now comes from `eligibility_off`

That is a much better match to the staged branch story.

## Interpretation

`runtime_r2b` now has a stronger research result than the earlier terminal-law
checkpoint.

What this pass established:

- the recovered local window is stable under a stricter causality test
- the `0.25` lock is not just scaffold autonomy
- eligibility is now a meaningful top-end causal gate in the packaged ablation

What still remains weak:

- the long-horizon coexistence-edge observable is still zero across the window
- `split_onset` is still `7/8` instead of `8/8`
- settled `0.25` eligibility remains small, so the mediating stage is real but
  spatially sparse in the final summary metrics

## Judgment

This branch now deserves continuation on its own terms.

The next justified move is no longer "fix the lock basin." That part is
meaningfully improved.

The next justified move is narrower:

- either harden `split_onset`
- or improve the observables so the recovered interface structure is measured
  more honestly than the current zero-valued coexistence edge metric allows

## Evidence

- [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_anchor_suite_v1/anchor_summary.csv)
- [assessment_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/assessment_summary.csv)
- [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/anchor_summary.csv)
