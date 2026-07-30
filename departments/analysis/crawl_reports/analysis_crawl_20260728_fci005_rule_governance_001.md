# Crawl Report: FCI-005 Rule Governance

## Scope

This bounded, read-only crawl examined the latest FCI-005 bridge rule evaluators, aggregation semantics, dependency-stage model, threshold matrix, and symbol import manifest.

## Directly observed

- Carrier, context, and provenance result types are defined.
- Complete applicable-rule aggregation is specified; unique-authority precedence must be explicit.
- Dependency stages and completeness-record requirements are specified.
- Threshold routes distinguish `ABSENT`, `UNDEFINED`, `INVALID`, and `VALID`, including conflict handling.
- Exact symbol-level imports and supersession metadata are present.

## Remaining blockers

No independently governed carrier-mapping rules, context-mapping rules, or dependency completeness records are instantiated for witness use. Therefore bridge tests 001, 002, 004, and 005 remain open, and witness fixtures must not be fabricated.

## Assessment

The evaluator architecture is structurally specified at C1 model-relative level, but the source-to-observation bridge is not established. This is not empirical evidence or a semantic-preservation result.

## Recommendation

Identify or authorize governed mapping-rule records and an independent dependency extractor before constructing any witness fixtures.

No canonical registry, textbook, `BCon_x`, `H_x`, or `delta_a` surface was modified.
