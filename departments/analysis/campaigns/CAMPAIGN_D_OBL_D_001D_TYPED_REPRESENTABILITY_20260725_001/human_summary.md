# OBL-D-001D Typed Representability Candidate

## Scope

This campaign defines and independently checks a provisional representability predicate using typed projected values, a typed relation witness, compatible trace, and explicit history.

## Directly observed

Eight hand-authored fixtures passed: one positive case, four negative cases, two boundary cases, and one matched-image history case. The validator does not use outcome labels to determine representability.

## Candidate rule

`RepDist_C(p,q,w,t,h)` is true only when both projected values have the declared projection type, the witness is typed, the trace is compatible, and required history is present.

## What this supports

The bounded fixture set supports rejecting projection-only and outcome-label-only proxies. It demonstrates that missing witness, wrong type, incompatible trace, and omitted history can be treated as distinct negative conditions under the candidate rule.

## Limitations

The fixtures are finite and hand-authored. The component semantics are not mechanized, no external validation was performed, and this result does not establish preservation under `Pi_D,C` generally.

## Status

`PASS_BOUNDED_CANDIDATE_VALIDATION`. `OBL-D-001D` remains `OPEN`. Human review and independent formal acceptance remain required. `OBL-D-001E` remains downstream.

## Actions not taken

No canonical math file, registry, theorem status, axiom, textbook wording, or obligation status was changed.
