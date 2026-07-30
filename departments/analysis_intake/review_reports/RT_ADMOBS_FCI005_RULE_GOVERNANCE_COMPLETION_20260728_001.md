# FCI-005 Rule Governance Completion Scaffold

Rule-level branch evaluators and complete applicable-rule aggregation are now explicit for carrier and context mappings. A governed unique-authority exception is permitted only when precedence is explicit.

The threshold route matrix is exhaustive over `VALID`, `INVALID`, `ABSENT`, and `UNDEFINED`; conflicting valid/invalid routes produce `INCONSISTENT`, while unresolved routes remain `UNDEFINED`.

Dependency stages now have an explicit order, and `DependencyGraphCompletenessRecord_x` is required before a pre-`RefOrient` result can be accepted. An exact symbol import manifest records source artifacts, digests, import mode, local symbols, and supersession.

Witness fixtures and bridge tests remain held. `BCon_x` is unbound and `H_x` undeclared.
