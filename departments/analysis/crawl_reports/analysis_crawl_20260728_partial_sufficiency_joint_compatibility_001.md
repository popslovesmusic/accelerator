# Crawl Report: Partial Sufficiency and Joint Compatibility

## Scope

This bounded, read-only crawl examined `PartialSufficiencyWitness_x`, `PermittedResolution_x`, `JointlyCompatible_x`, and related orientation-family structures.

## Directly observed

- `O_adm` exists as an admissible orientation family in the orientation-selection material.
- `W_adm` exists as an admissible orientation window over an explicit context.
- `C_orient` exists as a candidate coherence metric over admissible orientation assignments.
- No direct governed definition of `JointlyCompatible_x`, `HigherOrderCompatible_x`, or `PairwiseSufficiency_x` was found in the inspected materials.

## Inferred inside the provisional model

`JointConstraint_x` remains provisionally structured as:

`PairwiseCompatible_x AND HigherOrderCompatible_x`

A bounded three-orientation fixture shows why pairwise compatibility cannot be assumed sufficient: every pair may be compatible while the complete family violates a higher-order constraint.

## Open obligations

1. Define the domain and source of higher-order family constraints.
2. Determine whether `O_adm` or `W_adm` can be mapped into the provisional family type without rebinding existing symbols.
3. Establish or falsify pairwise sufficiency for the declared RT domain.

## Support and uncertainty

Support level: C1 model-relative, definition-level analysis. The relationship to `C_orient` is supporting-only; `C_orient` is not treated as a compatibility predicate. No theorem, physical-law, or empirical claim is made.

## Recommendation

Prepare a human-review type-mapping proposal for `O_adm`/`W_adm` and a `PairwiseSufficiency_x` proof-or-counterexample obligation.

No canonical registries, textbook content, `delta_a`, or D-semantics obligations were modified.
