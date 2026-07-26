# OBL-D-001D Independent Check — 2026-07-26

## Result

The existing validator and a separate PowerShell implementation independently classified all eight hand-authored fixtures identically: 8 passed, 0 failed.

## What is supported

The declared conjunction distinguishes typed projected values, typed witness, compatible trace, and explicit history. The matched-image/history negative control remains rejected, and outcome labels are not used as predicate inputs.

## Status boundary

`PASS_BOUNDED_INDEPENDENT_CHECK` with `MECHANICALLY_VERIFIED` evidence for the finite checker result. `OBL-D-001D` remains `OPEN_WITH_BOUNDED_INDEPENDENT_SUPPORT` because the component semantics themselves have not received formal acceptance and the projection route was not mechanized.

The combined D-semantics gate remains `BLOCKED_NOT_READY`; OBL-D-001E remains open and dependent.

## Next action

Obtain formal acceptance of the four component predicates, then rerun the combined D-semantics gate.

No theorem, axiom, or external physical claim is promoted.
