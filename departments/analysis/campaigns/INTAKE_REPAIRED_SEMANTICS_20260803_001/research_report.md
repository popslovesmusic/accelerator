# Repaired Semantics Campaign

## Scope

This C1 campaign tests explicit repairs for the countermodels found in the preceding adversarial campaign. The earlier countermodels remain immutable.

## Directly observed/defined

All 10 repaired finite-semantic checks passed:

- 056 now has typed `SUCCESS`, `EMPTY_ADMISSIBLE_FAMILY`, and `INVALID_BOUNDARY` outcomes.
- 057 requires explicit context and preserves typed inversion identity.
- 060 uses a deterministic MTO selector, retains aspect history separately, preserves OTM multiplicity, and applies a depth termination condition.

## Inferred inside framework

The repaired candidate semantics discharge the specific finite countermodels previously identified. They provide a more explicit operational scaffold for further testing.

## External resemblance (Analogy only)

The repairs resemble typed error channels, deterministic rewriting, provenance retention, multiset decomposition, and bounded recursion. These are analogies only.

## What it does NOT prove

Passing repaired finite checks does not establish general uniqueness, completeness, theorem status, physical validity, or canonical admission. It does not prove that these repairs are the only lawful repairs.

## Failure modes / uncertainty

The repair rules are candidate semantics selected after exposure of the prior countermodels. They require fresh independent model-class testing and may fail under broader domains.

## Status

`PASS_REPAIRED_FINITE_SEMANTICS`, 10/10 checks. All intake entries remain C1/HOLD_C1.
