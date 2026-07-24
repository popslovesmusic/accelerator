# Negative Case Report

## Scope
This report records the negative fixtures that bound `OBL-D-001C`.

## Directly observed/defined
- `D-C-WRONG-CODOMAIN-001` rejects any codomain other than `TYPE_PROJECTION_C`.
- `D-C-DIRECT-SUBSTITUTION-001` rejects direct substitution from `A|E` to `D(*|*)`.
- `D-C-UNTYPED-SOURCE-001` rejects an untyped source.

## Inferred inside framework
The current C packet supports a typed route only when the source, operator invocation, and codomain are all explicitly declared.

## External resemblance
This resembles a type-safety boundary, but it is only a local governed proof packet.

## What it does NOT prove
It does not prove semantic preservation, injectivity, reversibility, or complete information preservation.

## Failure modes / uncertainty
Any future accepted counterexample to the negative fixtures reopens `OBL-D-001C`.
