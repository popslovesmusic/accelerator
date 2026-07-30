# FCI-005 Bridge Semantic Completion Scaffold

The bridge support now has independently typed result states:

- `CarrierBridgeResult_x`: `REPRESENTED`, `NOT_REPRESENTED`, `UNDEFINED`;
- `ContextBridgeResult_x`: `CONTEXT_ALIGNED`, `CONTEXT_MISMATCH`, `UNDEFINED`;
- `EffectiveThresholdResult_x`: `VALID`, `INVALID`, `UNDEFINED`, `INCONSISTENT`.

`BridgeWitnessRecord_x` now separates left-carrier, right-carrier, context, and dependency provenance. `DependencyStageEvidence_x` requires a transitive pre-`RefOrient` graph with no prohibited downstream ancestors.

Import symbols and supersession precedence are explicit. The evaluator subsuite remains definition-level passing, but bridge tests 001, 002, 004, and 005 remain held because no governed source witness fixtures may be fabricated.

`BCon_x` remains unbound, `H_x` remains undeclared, and `delta_a` is unchanged.
