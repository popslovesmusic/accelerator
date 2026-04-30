# Runtime R2B Assessment And Plan v1

Generated: 2026-03-24

## Scope

This note opens `runtime_r2b` as a research-only non-scalar successor to
frozen `runtime_r2`.

## Why This Branch Exists

`runtime_r2` answered one useful question and failed one important one.

It showed:

- directional coexistence can be represented explicitly
- a short-horizon corridor-like transient is real

But it failed the packaged local-window test because the full vector law
collapsed almost everything in the `0.08 .. 0.25` window into universal
scaffold lock.

The specific failure interpretation was:

- coexistence recognition
- split pressure
- scaffold commitment

were too tightly collapsed into one over-eager right-side nucleation path.

## Design Choice

`runtime_r2b` keeps the vector node state but changes the stage logic.

The intended sequence is now:

1. raw coexistence recognition
2. slow split eligibility
3. tension growth from eligibility
4. scaffold commitment from eligibility plus tension

This is the smallest non-scalar redesign that directly tests whether the
`runtime_r2` failure was caused by stage collapse rather than by vector state
itself.

## Evaluation Frame

The branch uses the same packaged local-window anchors:

- quiet reference `0.08`
- first precursor `0.10`
- middle precursor `0.14`
- corridor interior `0.20`
- split onset `0.23`
- split center `0.24`
- barrier lock `0.25`

The first pass should answer:

1. Does the left side stay quieter than in `runtime_r2`?
2. Does split eligibility become visible before full scaffold lock?
3. Does `eligibility_off` remove right-side emergence more specifically than
   `scaffold_off`?
4. Does frozen `runtime_r2` universal lock materially weaken?

## Research Discipline

`runtime_r2b` is not an authority branch.

The correct outputs are:

- a stage-anchor package
- a stage-causality package
- an insight report

The incorrect outputs are:

- authority claims
- PDE mapping
- promotion language

## Immediate Plan

1. Finish the stage-gated vector kernel conversion.
2. Run the anchor suite on the packaged local window.
3. Run the causality suite with `eligibility_off` and `scaffold_off`.
4. Write the first insight report and decide whether the branch deserves
   continuation.
