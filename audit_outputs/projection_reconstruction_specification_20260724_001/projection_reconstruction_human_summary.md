# Projection Reconstruction Specification

## Result
Specification status: `PASS_PARTIAL_REQUIRES_MAPPING_RESOLUTION`. 14 retained legacy production tables received deterministic generation specifications.

## Unresolved mappings
2 field mappings remain open because semantic equivalence between the normalized source-corpus candidate and legacy projections is not established. No silent defaults are specified.

## Determinism
The plan pins source manifest, schema/spec/tool versions, normalization, ordering, timezone, and null semantics.

## Execution order
Bootstrap source metadata first, then identifiers and projections, followed by derived tables, indexes, and views.

## Equivalence
Tests cover identity, provenance, relationships, behavior, and representation; row counts alone are explicitly insufficient.

## Production safety
The plan creates only a versioned non-production candidate. Legacy and source corpus remain immutable; cutover requires separate human approval.
