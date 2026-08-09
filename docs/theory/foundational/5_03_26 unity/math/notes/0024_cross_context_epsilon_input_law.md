# Cross-Context `epsilon_a` Input Law Candidate

## Status

`DEFINITION_CANDIDATE`

- Governing obligation: `OBL-D-001E`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Scope: bounded contexts with declared threshold inputs.

## Threshold inputs

Let each context provide a declared input profile:

```text
Q_C := (a_C, d_C, m_C)
```

where `a_C` is the admissibility floor, `d_C` is the distinction-structure class, and `m_C` records the minimum-semantics mode (`EXACT_MINIMUM` or `INFIMUM_CANDIDATE`). A bounded threshold candidate is:

```text
epsilon_{a,C} := F(Q_C)
```

with `F(Q_C) = a_C` only when `a_C > 0` and the mode is admissible for the declared case. Empty or nonpositive profiles return undefined/rejected rather than zero.

## Conditional cross-context law

The bounded law tested here is conditional:

```text
Q_C = Q_C'  =>  epsilon_{a,C} = epsilon_{a,C'}
```

No equality is asserted when profiles differ. Thus the model rejects an unconditional universal threshold constant while allowing equal thresholds under equal declared inputs.

## Limits

The input profile is declared rather than derived from a universal admissibility theory. The law is bounded and conditional; it does not discharge OBL-D-001E or establish cross-context universality.
