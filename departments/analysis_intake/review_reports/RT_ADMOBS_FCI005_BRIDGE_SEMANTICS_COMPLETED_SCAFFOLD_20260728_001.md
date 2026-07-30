# FCI-005 Independent Bridge Semantics Scaffold

The scaffold now defines branch-result semantics for carrier representation, context alignment, dependency stage, threshold routes, and witness validation.

Carrier and context mappings distinguish definite success, definite failure, and unresolved evaluation. Dependency evidence uses a directed graph with explicit node, edge, stage, and provenance fields. Threshold routes distinguish `ABSENT` from `UNDEFINED` and preserve `INCONSISTENT` conflicts.

Witness validity is evaluated independently through typed results; the witness cannot validate itself by merely naming a mapping rule. Imports are symbol-exact with explicit supersession rules.

Witness fixtures remain unauthorized and bridge tests remain held. `BCon_x` is unbound, `H_x` undeclared, and `delta_a` unchanged.
