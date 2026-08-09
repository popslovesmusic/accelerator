# D/E Clean-Room Equivalence Obligations — Bounded Formalization

Status: `C1_DEFINED_PROVISIONAL` — additive obligation formalization; no existing lemma or proof is modified.

## Scope

This note formalizes the bounded comparison obligations for the frozen Notebook 26 authoritative candidate-comparison design. It does not provide a candidate implementation, prove equivalence, discharge `OBL-D-001D` or `OBL-D-001E`, or elevate any claim ceiling.

## Typed comparison objects

Let `D_26` be the finite corpus of records accepted by the frozen Notebook 26 schema. Let:

- `G : D_26 -> Y` be the exact governed frozen candidate, when candidate provenance, implementation identity, and SHA-256 are supplied;
- `O : D_26 -> Y` be the clean-room declarative oracle defined by `RT_D_E_INDEPENDENT_FORMAL_ORACLE_SPEC_20260731_001`;
- `N : Y -> Y'` be the declared output normalization used for comparison and replay;
- `Q : D_26 x D_26 -> {0,1}` be the declared corpus-membership and validity predicate;
- `F_j : D_26 -> D_26` be each of the 25 declared fault-family transformations where its preconditions hold.

The bounded comparison predicate is:

```text
Eq_26(G,O,D_26) := forall r in D_26, Q(r) -> N(G(r)) = N(O(r))
```

The bounded replay predicate is:

```text
Replay_26(G,O,D_26) := digest(N(G(D_26))) = digest(N(G(shuffle(D_26))))
                       and digest(N(O(D_26))) = digest(N(O(shuffle(D_26))))
```

For each valid fault-family transformation, the metamorphic obligation is:

```text
Meta_j(G,O,r) := Expected_j(r, G(r), G(F_j(r)))
                 and Expected_j(r, O(r), O(F_j(r)))
```

The bounded campaign result is admissible only when candidate identity, oracle capture, corpus serialization, all required hashes, and clean-room review prerequisites pass before execution.

## Obligations

1. **Candidate provenance:** supply the exact governed candidate source, implementation ID, source path, SHA-256, and declared result vocabulary.
2. **Oracle independence:** demonstrate that `O` is derived from the frozen specification and does not import candidate code, prior subject functions, or reference-stand-in adapters.
3. **Domain closure:** show that every generated record and transformed record satisfies `Q` or is explicitly classified as an invalid/rejection case.
4. **Normalization determinacy:** freeze `N` before execution and preserve both raw and normalized outputs.
5. **Comparison completeness:** execute every declared comparison unit across the finite corpus twice, including shuffled replay.
6. **Falsification preservation:** retain every disagreement, invariant failure, hash mismatch, missing prerequisite, and out-of-domain counterexample; do not collapse them into a pass.
7. **Interpretation boundary:** even if all bounded obligations pass, classify the result no higher than the design’s C2 limitation ceiling and do not infer universal equivalence or theorem closure.

## Current disposition

The clean-room self-test satisfies only implementation-health checks. Notebook 26 results used a reference stand-in and therefore do not instantiate `G`. Obligations 1, 2, and 5 remain unexecuted. The campaign is blocked pending candidate provenance and clean-room reviewer sign-off.

## Falsification conditions

Any candidate/oracle disagreement, transformation contradiction, order-dependent replay digest, candidate/specification hash mismatch, incomplete corpus, shared implementation dependency, or missing review prerequisite falsifies the bounded comparison package and reopens the relevant obligation.

## Non-authorizations

This note authorizes no execution, candidate import, theorem promotion, claim promotion, external interpretation, or conclusion about universal D/E semantics.
