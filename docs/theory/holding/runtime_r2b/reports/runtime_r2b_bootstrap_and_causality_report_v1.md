# Runtime R2B Bootstrap And Causality Report v1

Generated: 2026-03-24

## Scope

This report records the first full evaluation of `runtime_r2b`, the
stage-gated non-scalar successor to frozen `runtime_r2`.

The branch question was narrow:

- if coexistence recognition, split eligibility, and scaffold commitment are
  separated into stages, does the `runtime_r2` universal-lock failure weaken
  into a more informative local window?

## Methods

The branch reused the same packaged local-window anchors as `runtime_r1c` and
`runtime_r2`:

- quiet reference `0.08`
- first precursor `0.10`
- middle precursor `0.14`
- corridor interior `0.20`
- split onset `0.23`
- split center `0.24`
- barrier lock `0.25`

The vector kernel was changed in one specific way relative to `runtime_r2`:

- raw coexistence no longer drives scaffold directly
- a slow `split_eligibility` field is written from coexistence recognition,
  corridor context, and local diffusion
- tension grows from `split_eligibility`
- scaffold grows from `split_eligibility` plus tension

Evaluation packages:

- anchor suite:
  - [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_anchor_suite_v1/anchor_summary.csv)
- causality suite:
  - [assessment_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/assessment_summary.csv)
  - [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/anchor_summary.csv)

I also checked representative transient traces at:

- [run_timeseries.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/full/corridor_interior/seed_20401/run_timeseries.csv)
- [run_timeseries.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/full/split_onset/seed_20401/run_timeseries.csv)

## Results

### 1. The branch is real at short horizon

The smoke run did not start in immediate wall lock. At `1024` steps, the
branch produced a corridor-like transient:

- regime `directional_corridor_candidate`
- `mean_abs_output = 1.262207`
- `corridor_edge_fraction = 0.804688`
- `mean_split_eligibility = 0.000011`
- `mean_barrier_scaffold = 0.068432`

Evidence:

- [run_metrics.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/build/smoke_output/run_metrics.csv)

So the redesign was not null. It did delay the old lock behavior.

### 2. Long-horizon anchor behavior still collapses completely

The packaged local window still ends in universal scaffold lock at every anchor.
From [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_anchor_suite_v1/anchor_summary.csv):

- all seven anchors: `lock_count = 8`
- all seven anchors: `mean_barrier_edge_fraction = 1`
- all seven anchors: `mean_barrier_scaffold = 3`
- all seven anchors: `mean_split_eligibility = 0`

That means the stage-gated law did not recover a meaningful internal window at
long horizon.

### 3. The transient is only temporary

Representative time traces show the same three-stage collapse on both the
corridor and right-side anchors:

1. early corridor-like organization around `1024` steps
2. mixed partial collapse by `2048`
3. low-activation universal lock by about `3072`

At `split_onset`, seed `20401`, the trace is:

- `1024`: corridor edge `0.773438`, barrier edge `0.062500`,
  `mean_split_eligibility = 0.000008`
- `2048`: corridor edge `0.296875`, barrier edge `0.625000`,
  `mean_split_eligibility = 0.000232`
- `3072`: corridor edge `0`, barrier edge `1`,
  `mean_split_eligibility = 0.000001`
- `4096+`: stable low-activation lock, scaffold `3`, tension `2.571429`,
  eligibility `0`

So the new field does rise briefly, but it never becomes a durable intermediate
stage. It disappears before the branch settles.

### 4. Causality is cleaner than `runtime_r2`, but still negative

The causality suite shows a strong separation:

- `full` ends in complete barrier lock
- `eligibility_off` removes the barrier side entirely
- `scaffold_off` behaves the same way

From [assessment_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/assessment_summary.csv):

- for `corridor_interior`, `split_onset`, `split_center`, and `barrier_lock`:
  - `full_barrier = 1`
  - `eligibility_off_barrier_delta = -1`
  - `scaffold_off_barrier_delta = -1`
  - `full_split_eligibility = 0`

This means the stage logic is at least causally interpretable:

- scaffold lock still depends on the eligibility path
- but the eligibility path never survives as a visible state at long horizon

## Interpretation

`runtime_r2b` improved one thing and failed the larger goal.

What improved:

- the branch no longer looks like immediate direct coexistence-to-lock collapse
- there is a real short-horizon corridor-like transient
- the staged path is causally cleaner than frozen `runtime_r2`

What failed:

- the long-horizon local window is still universal scaffold lock
- split eligibility is not a durable intermediate stage
- the left side does not stay quiet or precursor-like
- the right side does not preserve a coexistence band before lock

The clearest interpretation is:

- stage gating delays the old failure
- it does not change the terminal basin
- tension plus scaffold still form an over-eager absorbing wall attractor
- eligibility acts like a transient trigger, not a sustained stage carrier

## Judgment

`runtime_r2b` is useful as a research checkpoint, but not promotable.

It does not recover a meaningful local stage window, and it does not beat the
frozen `runtime_r2` question strongly enough to justify a longer tuning line.

## Next Justified Move

Not more `runtime_r2b` tuning.

If this vector research line continues, the next justified move should be a
different principle:

- a branch where scaffold has independent stage logic instead of being a late
  absorbing sink
- or a branch where tension cannot remain high once directional activation has
  collapsed

In other words, the next research successor should target the lock basin
directly, not just delay the route into it.
