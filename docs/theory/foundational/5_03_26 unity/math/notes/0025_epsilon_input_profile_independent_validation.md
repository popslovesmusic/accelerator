# Independent Validation of `epsilon_a` Input Profiles

## Status

`VALIDATION_CANDIDATE`

- Governing obligation: `OBL-D-001E`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Scope: independent finite validation of declared profile inputs.

## Validation rule

For an exact-minimum profile `Q_C = (a_C,d_C,EXACT_MINIMUM)`, the declared floor is accepted only when:

```text
a_C > 0
and A_C is nonempty
and a_C = min(A_C)
```

Profiles with empty sets, nonpositive floors, or mismatched exact floors are rejected. An infimum-candidate profile is retained as unresolved and is not treated as exact validation.

## Cross-context check

Two contexts are eligible for equal-threshold comparison only when their validated profile tuples `(a_C,d_C,m_C)` are identical. The validation does not infer equality from context names alone.

## Limits

The admissible distinction sets and profile classes are supplied finite inputs. This validates internal consistency of the declared profiles; it does not derive them from a universal admissibility theory or discharge OBL-D-001E.
