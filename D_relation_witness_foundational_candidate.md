# Foundational Theory Draft: Context-Indexed Relation Witnesses

**Status**: NON_CANONICAL_FOUNDATIONAL_CANDIDATE  
**Domain**: D_SEMANTICS  
**Blocked Obligation**: OBL-D-001D  

---

## 1. Scope
This document specifies the algebraic and semantic structure of context-indexed relation witnesses under context `C` for the Mono-Process Framework. It is a non-canonical candidate draft.

---

## 2. Semantic Layers
To avoid ontological conflation, five distinct semantic layers are defined:
- **L0 (Context)**: Context parameter `C`.
- **L1 (Relational objects)**: Relations, distinctions, and semantic relation witnesses.
- **L2 (Witness realizations)**: Trace certificates, Lean proof terms, and executable artifacts.
- **L3 (Validation judgments)**: `TypedWitness_C`, `RepDist_C`, `TraceCompatible_C`.
- **L4 (Transition preservation)**: Admissible transitions, witness transport, and representation preservation.

---

## 3. Primitive Objects
- `C` (context): Universe `ContextUniverse`.
- `Expr_D`: Domain of whole participation expressions.
- `TYPE_PROJECTION_C`: Target projection type in context `C`.
- `TYPE_WITNESS_C`: Set of relational witnesses in context `C`.

---

## 4. Candidate Signatures
- `Rel_C : TYPE_PROJECTION_C x TYPE_PROJECTION_C x TYPE_WITNESS_C -> Prop`
- `Dist_C : Expr_D x Expr_D -> Prop`
- `TypedWitness_C : TYPE_WITNESS_C -> Prop`
- `RepDist_C : TYPE_PROJECTION_C x TYPE_PROJECTION_C x TYPE_WITNESS_C -> Prop`
- `Realizes_C : TYPE_REALIZATION x TYPE_WITNESS_C -> Prop`
- `TraceCompatible_C : TYPE_TRACE x TYPE_WITNESS_C -> Prop`
- `Transport_C : TYPE_TRANSITION x TYPE_WITNESS_C x TYPE_WITNESS_C -> Prop`

---

## 5. Formation Rules
- `RepDist_C(p, q, w)` is well-formed only if `p` and `q` are typed as `TYPE_PROJECTION_C` and `w` is typed as `TYPE_WITNESS_C`.
- `TraceCompatible_C(t, w)` is well-formed only if `t` is typed as `TYPE_TRACE` and `w` is typed as `TYPE_WITNESS_C`.

---

## 6. Judgments
- `RepDist_C(p, q, w) iff type(p) = TYPE_PROJECTION_C ∧ type(q) = TYPE_PROJECTION_C ∧ TypedWitness_C(w) ∧ Rel_C(p, q, w) ∧ TraceCompatible_C(w)`
- `TypedWitness_C(w)` holds if `w` is relationally valid under context `C`.

---

## 7. Relation Witness Algebra
- **Witness Identity**: Intensional and relational, independent of concrete realizations.
- **Witness Equivalence**: Explicitly context-indexed `=_w,C`.
- **Composition**: Partial and context-preserving composition `w1 ∘ w2` is defined only on matching relation boundaries.
- **Transport**: Partial mapping across admissible transitions.
- **Restriction**: Restricting a witness from `C` to subset context `C'` is monotone.
- **Extension**: Extension of witnesses to broader contexts is generally invalid.

---

## 8. Realization Semantics
Concrete realizations (L2) such as Lean proof terms, trace certificates, and executable artifacts map to abstract semantic witnesses (L1) via `Realizes_C`. Soundness is required:
`Realizes_C(r, w) ∧ Valid(r) → TypedWitness_C(w)`
Completeness is not assumed.

---

## 9. Trace Compatibility
`TraceCompatible_C(t, w)` is explicitly indexed by context `C` (DEC-SEM-002). It evaluates to true if and only if trace `t` satisfies the relational boundaries of `w` in `C`.

---

## 10. Witness Transport
`Transport_C(tau, w, w')` defines the transport of witness `w` to `w'` under transition `tau`. It is a partial relation; transport can fail even when type preservation (OBL-D-001C) succeeds.

---

## 11. Candidate Axioms
- `AX-WITNESS-REPDIST`: `Rel_C(p, q, w) ∧ TypedWitness_C(w) ∧ TraceCompatible_C(w) → RepDist_C(p, q, w)`
- `AX-REALIZATION-WITNESS`: `Realizes_C(r, w) ∧ ValidRealization(r) → TypedWitness_C(w)`
- `AX-TRANSPORT-PRESERVATION`: `RepDist_C(Pi_D,C(x), Pi_D,C(y), w) ∧ Transport_C(tau, w, w') → RepDist_C(Pi_D,C(x'), Pi_D,C(y'), w')`

---

## 12. Candidate Lemmas
- `LEMMA-CONTEXT-RESTRICTION`: If `C' ⊆ C` and `TypedWitness_C(w)` holds, then `TypedWitness_C'(w)` holds.

---

## 13. OBL-D-001D Formability
The obligation can be stated as:
`∀ x y w tau w', RepDist_C(Pi_D,C(x), Pi_D,C(y), w) ∧ AdmissibleTransition(tau, x, x') ∧ AdmissibleTransition(tau, y, y') ∧ Transport_C(tau, w, w') → RepDist_C(Pi_D,C(x'), Pi_D,C(y'), w')`

---

## 14. Rejected Alternatives
- Context-free trace compatibility (rejected by DEC-SEM-002).
- Equating `TypedWitness_C` with a single realization class such as trace certificates (rejected by DEC-SEM-001).

---

## 15. Open Questions
- Is `Rel_C` context-free or context-indexed for all contexts?
- Does `project_w` preserve witness uniqueness?

---

## 16. Source Traceability
- `docs/theory/foundational/5_03_26 unity/math/notes/0014_d_representable_distinction_candidate.md`
- Resolutions `DEC-SEM-001` and `DEC-SEM-002`.

---

## 17. Canonicalization Requirements
To elevate this draft to canonical status:
1. Formally define `TYPE_WITNESS_C` in the math type registry.
2. Formally define `project_w` signature and axioms in Lean.
3. Rerun the validation gate.
