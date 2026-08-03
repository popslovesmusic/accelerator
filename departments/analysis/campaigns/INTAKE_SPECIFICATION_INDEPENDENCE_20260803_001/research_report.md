# Specification-Independence Audit

## Scope

This C1 audit compares the repaired semantics with deliberately different finite semantic choices. It tests whether prior passes are invariant to specification choice.

## Directly observed/defined

All four comparison tests diverged:

- 056: exclusion-all-but-one versus exclusion-of-one produce different admissible families.
- 057: full typed equality versus relation-only equality disagree on context identity.
- 060: lexicographic MTO selection versus frequency-ranked selection produce different outputs.
- 060: depth-based termination versus cycle-based termination produce different continuation traces.

Result: `SPECIFICATION_DEPENDENCE_FOUND`, 4/4 divergences.

## Inferred inside framework

The prior finite passes are valid only relative to explicitly chosen repair semantics. They do not identify a unique semantics from the intake text alone.

## External resemblance (Analogy only)

This resembles specification sensitivity in operational semantics and model-theoretic underdetermination. It is an analogy only.

## What it does NOT prove

Specification dependence does not falsify every possible RT formulation. It shows that the current intake material underdetermines the tested choices.

## Failure modes / uncertainty

The alternate semantics are finite comparison models, not an exhaustive survey of all lawful interpretations.

## Status

`SPECIFICATION_DEPENDENCE_FOUND`. C1/HOLD_C1 remains mandatory. The next action is to freeze semantic choices explicitly before further validation or promotion.
