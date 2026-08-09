# Provisional FCI-004 / FCI-005 Overlap Analysis

## Result

The candidates are classified as a `SPECIALIZATION_CANDIDATE`.

FCI-004 (`O_b` composed with `O_a`) is orientation-specific and requires typed admissible continuation, distinction preservation, closure-class preservation, and compatible orientation classes.

FCI-005 (`otimes`) is a broader typed partial-composition operator over operands and context. It includes typing, distinction-floor, admissibility, residue, closure-class, and context-bound composition guards.

The shared logical effect is compatible with FCI-004 being an orientation-specific projection of FCI-005, but the required type bridge has not been established. FCI-004 and FCI-005 therefore remain separate provenance records, and no member is bound into `BCon_x`.

## Required bridge tests

1. Map `O_a` and `O_b` to the `Omega_obs` orientation type.
2. Map the FCI-004 context to `B_x`, `D_rel`, and `R` before `RefOrient` or `ProjectBounded`.
3. Show that all FCI-004 failure guards survive projection.
4. Ensure `otimes` is not rebound as a family-level or higher-order predicate.

`H_x` remains undeclared. No canonical or semantic surface was modified.
