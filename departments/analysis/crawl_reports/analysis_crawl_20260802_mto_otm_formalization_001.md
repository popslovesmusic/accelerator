# MTO/OTM Calculus Formalization Assessment

## Campaign Purpose

Develop a bounded, noncanonical typed model for the inducted MTO/OTM proposal and identify the minimum definitions and tests required before any canonical mathematical treatment.

## Result

`PARTIAL_SUCCESS`. The proposal supports a useful candidate typing boundary, but its equivalence, determinism, totality, and decomposition claims remain unresolved.

## Candidate Model

- `Primitive` is represented provisionally as `P`.
- `Aspect` is represented as a context-indexed organization `A[C, P*]`.
- `RT` is represented as a resolved object `R`.
- Candidate MTO signature: `MTO_C : AdmissibleAspect_C^n -> RT_C`.
- Candidate OTM signature: `OTM : RT_C -> PrimitiveMultiset`.

The context index is necessary because an expression such as `2+2` may participate as a computational aspect in one context and as an observed analysis condition in another. That is a role distinction, not evidence that the objects are automatically identical.

## Main Findings

1. MTO needs an explicit admissibility domain, arity, orientation compatibility, and failure semantics.
2. Aspect role must be context-indexed before computational and analysis uses can be compared.
3. OTM should conservatively return a primitive multiset or another structure that preserves multiplicity until set-losslessness is established.
4. The proposed MTO-output equivalence is conditional. Equal outputs do not establish equivalence until RT identity/equivalence and deterministic MTO selection are defined.
5. Orientation resolution requires a typed selector, comparison rule, tie-breaking rule, and explicit non-resolution behavior.

## Fixtures

Positive fixtures cover computational and analysis-role aspects and OTM primitive decomposition. Rejection fixtures cover untyped role reuse, output-equality overreach, historical aspect recovery, multiplicity loss, and implementation-order tie-breaking.

## Open Obligations

The next evidence should define `AdmissibleAspect_C`, context-indexed roles, RT identity/equivalence, deterministic MTO selection, OTM multiplicity semantics, and orientation resolution. These remain research obligations, not canonical definitions.

## What Was Not Established

This assessment did not prove identity-destructive closure, aspect equivalence, recursive RT calculation, a unique orientation field resolution, or any external physical interpretation. The source remains `NOT_REVIEWED`, `HOLD_C1`, and `NON_CANONICAL_CANDIDATE`.

## Recommended Next Action

Build an independent finite fixture evaluator for role-indexed aspects, deterministic MTO candidates, and OTM multiplicity preservation. Stop when all positive/rejection fixtures execute deterministically or a counterexample reopens the corresponding obligation.
