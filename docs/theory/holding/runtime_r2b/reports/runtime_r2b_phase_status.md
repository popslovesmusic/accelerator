# Runtime R2B Phase Status

Updated: 2026-03-25

## Branch Role

`runtime_r2b` is a research-only non-scalar successor to frozen `runtime_r2`.

Its role is still narrow:

- test whether staged split eligibility can preserve a real local window
- test whether a different scaffold/tension terminal law can replace the old
  all-window absorbing lock basin

## Current Branch State

`runtime_r2b` is active again as a research branch.

It now passes:

- quiet, precursor, and corridor anchors stay out of universal lock
- `0.23` and `0.24` now hold clean `8/8` split-stage packages
- `0.25` now produces a distinct scaffold-lock regime across all seeds
- `eligibility_off` and `scaffold_off` both remove the `0.25` lock candidate,
  with `eligibility_off` now producing the larger barrier reduction

It still does **not** pass:

- coexistence-edge observables remain near zero at long horizon
- split eligibility is still small in the settled `0.25` metrics, so it is a
  sparse mediator rather than a large durable final field
- the probe still relies on a pragmatic onset-support classifier because the
  original coexistence-edge observable remains too weak to carry the split readout

## Current Authority Files

- [README.md](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/README.md)
- [branch_charter.json](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/branch_charter.json)
- [runtime_r2b_assessment_and_plan_v1.md](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/reports/runtime_r2b_assessment_and_plan_v1.md)

## Current Evidence

- [runtime_r2b_bootstrap_and_causality_report_v1.md](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/reports/runtime_r2b_bootstrap_and_causality_report_v1.md)
- [runtime_r2b_freeze_report_v1.md](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/reports/runtime_r2b_freeze_report_v1.md)
- [runtime_r2b_terminal_law_report_v2.md](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/reports/runtime_r2b_terminal_law_report_v2.md)
- [runtime_r2b_terminal_law_report_v3.md](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/reports/runtime_r2b_terminal_law_report_v3.md)
- [runtime_r2b_onset_and_observables_report_v4.md](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/reports/runtime_r2b_onset_and_observables_report_v4.md)
- [anchor_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_anchor_suite_v1/anchor_summary.csv)
- [assessment_summary.csv](G:/MPF/orientation/level2/rerun_v23/analog/runtime_r2b/outputs/runtime_r2b_stage_causality_suite_v1/assessment_summary.csv)

## Current Interpretation

The preserved negative interpretation is no longer the whole story.

The branch now shows:

- centered diffusion plus support-gated collapse decay removed the old
  all-window absorbing lock basin
- a drive-separated local window is now visible:
  - corridor at `0.20`
  - split stage at `0.23` and `0.24`
  - scaffold lock at `0.25`
- the remaining problem moved upward:
  - `0.25` lock is now causally downstream of eligibility in the packaged
    ablations
  - onset robustness is acceptable now, but the observables are still weaker
    than the underlying stage structure

## Next Justified Move

Continue `runtime_r2b`, but constrain the next pass tightly.

The justified target is:

- preserve the current `0.20` to `0.25` ordering
- replace or supplement the zero-valued coexistence-edge observable with a
  better long-horizon interface readout
- decide whether the next branch move should be metric-facing only, or whether
  the kernel should expose a more explicit interface-carrier field
