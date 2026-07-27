# Independent Review: Source-Relation Counterexample

## Scope

This review checks whether the declared finite `Pi_D,C` prefix rule preserves source identity and relation identity in the tested representation.

## Directly observed/defined

Two source cases use distinct source identifiers and distinct relation identifiers, while sharing the same source and target values. Applying the declared C1 prefix rule produces the same projected source and target values for both cases. The checker recomputes this collision mechanically.

## Inferred inside framework

The finite candidate projection is non-injective with respect to the tested source-identity and relation-identity fields.

## External resemblance (Analogy only)

None asserted.

## What it does NOT prove

It does not establish universal information loss, rule out enriched projections, discharge D, discharge E, or support external claims.

## Decision

`BOUNDED_COUNTEREXAMPLE_CONFIRMED`. Both obligations remain `OPEN`; the claim ceiling remains `C1_DEFINED_PROVISIONAL`.
