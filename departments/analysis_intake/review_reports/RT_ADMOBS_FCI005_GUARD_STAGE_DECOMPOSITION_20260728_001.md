# Provisional FCI-005 Guard-Stage Decomposition

## Result

The full `otimes` guard set must not be projected into `BCon_x`.

### Conditional pre-admissibility candidates

- Operand and context typing.
- Distinction-floor condition `D(X|Z) > epsilon`, if its values are source-bound and available before reference construction.

### Prohibited downstream guard

- Nonempty `delta_a(X otimes_Y Z)` is downstream and potentially circular. It cannot enter `BCon_x` or the pre-resolution witness.

### Composition-law guard

Context-bound associativity governs chains of compositions and is not automatically a binary observation-assignment constraint.

### Unresolved guards

Result typing and closure-class compatibility require dependency inspection before classification. Aggregate failure branches must be decomposed individually because they mix pre-admissibility and downstream conditions.

`BCon_x` and `H_x` remain unbound/undeclared. No total transformation-to-observation map was introduced.
