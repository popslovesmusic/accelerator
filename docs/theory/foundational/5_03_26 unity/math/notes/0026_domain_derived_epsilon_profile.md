# Domain-Derived `epsilon_a` Profile

## Status

`DEFINITION_CANDIDATE`

- Governing obligation: `OBL-D-001E`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Scope: finite derivation from typed domain descriptors and raw distinction candidates.

## Derivation inputs

For context `C`, the descriptor supplies:

```text
T_C := (type_C, relation_C, raw_distinctions_C, admissibility_rule_C)
```

The domain-derived positive distinction set is:

```text
A_C := { d in raw_distinctions_C | admissibility_rule_C(d) = true }
```

For the bounded `positive_nonzero` rule, `A_C` contains only positive values. The threshold candidate is:

```text
epsilon_{a,C} := min(A_C)
```

when `A_C` is nonempty. The distinction-structure profile is retained from the typed relation descriptor and is not inferred from the numeric value alone.

## Rejection behavior

An untyped domain, incompatible relation descriptor, empty positive set, or nonpositive derived floor returns rejected/undefined. No input path realizes zero as an admissible threshold.

## Limits

The raw candidate sets and admissibility rules remain finite declared model inputs. This derives the threshold within the model but does not derive the domain descriptors from a universal theory, establish a universal cross-context law, or discharge OBL-D-001E.
