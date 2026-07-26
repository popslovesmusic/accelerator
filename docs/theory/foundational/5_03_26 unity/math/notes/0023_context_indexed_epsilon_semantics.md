# Context-Indexed `epsilon_a` Semantics

## Status

`DEFINITION_CANDIDATE`

- Governing obligation: `OBL-D-001E`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Scope: bounded threshold semantics with explicit exact-minimum and unresolved-infimum branches.

## Candidate typing

For a declared context `C` with admissible positive distinction set `A_C`, define the context-indexed threshold candidate:

```text
epsilon_{a,C} := min(A_C), when A_C is nonempty and an exact minimum is established.
```

If `A_C` is nonempty but only an infimum candidate is available, the threshold is retained as `INFIMUM_CANDIDATE` rather than silently promoted to an exact minimum. If `A_C` is empty, `epsilon_{a,C}` is undefined.

## Boundary semantics

The non-collapse predicate remains:

```text
distinction >= epsilon_{a,C} > 0
and participant_left != participant_right
```

The threshold is context-indexed and positive in the exact-minimum branch. No branch permits realized zero distinction.

## Limits

This note supplies a bounded semantic distinction between exact minimum and infimum candidate. It does not derive `A_C` from universal admissibility laws, establish threshold continuity across contexts, or discharge OBL-D-001E.
