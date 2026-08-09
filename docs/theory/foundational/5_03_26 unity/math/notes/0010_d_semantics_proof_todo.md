# D Semantics and Projection Proof TODO

## Scope

This task formalizes the local semantics of `D(A|B)` and the typed projection route to `D(*|*)`. It does not promote the notation to a universal operator or alter `RT_core`.

## Sequential checklist

- [x] Record the governed definition of `D(*|*)` as a projection of `A|E`.
- [x] Define a bounded context-indexed `Eval_D` contract.
- [x] State the typed transition route `A|E ->p Pi_D(A|E) -> D(*|*)`.
- [x] State proof obligations for typing, non-primitivity, representable-distinction preservation, and non-collapse.
- [ ] Discharge the obligations with a formal proof or independently checked model.
- [ ] Reassess theorem eligibility after obligation discharge.

## Current status

Definitions and proof obligations are registered as `C1_DEFINED_PROVISIONAL`. The package does not claim that `Eval_D` has a unique implementation, that `Pi_D` is injective, or that projection preserves all information in `A|E`.
