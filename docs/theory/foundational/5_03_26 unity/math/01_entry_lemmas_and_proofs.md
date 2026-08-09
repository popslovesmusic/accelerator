# Entry: Core Expression → Lemmas & Proof Sketches (Draft, 2026-05-05)

**Intent:** This document is the *math entry point* for the local series by extracting a small set of lemmas and proof sketches directly from the core biconditional update expression, while keeping assumptions explicit and isolating known gaps.

**Status:** Theoretical draft. These are *conditional* results: each lemma states exactly which definitions/assumptions it depends on.

---

## 0) Canonical core expression (indexed form)

We take as the starting point the indexed biconditional:

`Eα > 0  ⇔_residue  x'α = xα + Π_Aα ( Σ_{β ∈ csi(α)} transport(ωα, ωβ) )`

Reading:
- `Eα` is the existence scalar / total deviation magnitude for process `α`.
- `residue` indicates the biconditional is *history-gated* (it is not a bare logical equivalence).
- `Π_Aα` is a projection/filter operator onto the admissibility window `Aα`.
- `csi(α)` is the coherent source interface for `α` (the current coupling neighborhood).
- `transport(ωα, ωβ)` is the transport contribution from `β` to `α`.

This file stays at the level of the expression’s structural consequences; it does **not** assume a particular mechanism class (ODE/PDE/CA/etc.).

---

## 1) Definitions (minimal, “operator-first”)

**D1 (Admissibility window).** For each `α`, `Aα` is a subset of the space of candidate continuation increments (e.g. a subset of a tangent space at `xα`).

**D2 (Projection/filter).** `Π_Aα` is an operator acting on candidate increments such that:
- (Filter property) `Π_Aα(v) ∈ Aα` for all `v`.
- (Zero on inadmissible null) `Π_Aα(0) = 0`.

**D3 (Coupling neighborhood).** `csi(α)` is a set (possibly empty) of indices `β` that contribute to `α`’s update via transport.

**D4 (Transport contribution).** `transport(ωα, ωβ)` is an element of the same space as the admissible increments; it is additive under `Σ`.

**D5 (Residue-gated biconditional).** `⇔_residue` denotes a biconditional whose evaluation depends on a residue state. For this entry doc we use only the following: it is a *two-way constraint* between “existence active” and “update rule holds under current residue”.

---

## 2) Standing assumptions (explicit gaps are allowed)

These lemmas require only the following assumptions, unless a lemma states extra requirements.

- **A1 (Well-typedness):** all terms in the update expression are defined and lie in compatible spaces.
- **A2 (Admissibility is enforced pre-update):** `Π_Aα` is applied to the sum before adding to `xα`.
- **A3 (Biconditional closure intent):** the intended reading is genuine two-way closure: the “existence condition” and “update rule” must cohere under residue.

Known gaps (not resolved here):
- **G1:** an explicit oriented structure for `Aα` sufficient to derive `orientation` (the `−(i)` mechanism in the companion note).
- **G2:** an explicit definition of `transport(·,·)` sufficient to derive deviation propagation structure.
- **G3:** a formal closure rule for `csi(α)` membership (the admissibility-overlap proposal is a candidate, not assumed here).

---

## 3) Lemmas (structural consequences)

### Lemma 1 (Admissible increment)
For any `α`, the update increment
`Δxα := x'α − xα`
lies in `Aα`.

**Proof sketch.**
From the update rule,
`Δxα = Π_Aα( Σ_{β∈csi(α)} transport(ωα, ωβ) )`.
By D2 (filter property), the output of `Π_Aα` lies in `Aα`. ∎

---

### Lemma 2 (No-coupling fixed point under empty neighborhood)
Assume `csi(α) = ∅`. Then `x'α = xα`.

**Proof sketch.**
If the neighborhood is empty, the sum is the additive identity:
`Σ_{β∈∅} transport(ωα, ωβ) = 0`.
Then by D2, `Π_Aα(0)=0`, so the update rule gives `x'α = xα + 0 = xα`. ∎

---

### Lemma 3 (Participation boundary is a boundary condition, not “void”)
Assume `csi(α)=∅` and the update rule is the governing continuation rule when evaluated. Then `xα` is a fixed point of the continuation step, so “non-participating symmetry” can be treated as a boundary condition rather than an undefined state.

**Proof sketch.**
Immediate from Lemma 2: the continuation mapping sends `xα` to itself when no coupling contributions exist. ∎

---

### Lemma 4 (Pre-update constraint precedence)
If a candidate increment `v` contains inadmissible components, those components do not appear in `Δxα` as long as `Π_Aα` is applied before update addition.

**Proof sketch.**
This is the operational content of D2+A2: inadmissible components are removed/filtered prior to addition into state. ∎

---

### Lemma 5 (Closure reading constraint)
Any derived statement that uses only the update rule side must remain consistent when translated into a statement about the existence condition side, and conversely, under the same residue evaluation context.

**Proof sketch.**
This is a direct consequence of D5 + A3: `⇔_residue` is treated as a genuine two-way constraint, not as two independent implications. ∎

---

## 4) “M-law” correspondence (entry-level mapping)

This document does not re-derive the full M-law list; it provides the entry-level bridge:

- Lemma 2–3 correspond to the “boundary / fixed point” reading (M0-style).
- Lemma 1 and Lemma 4 capture the admissibility-window enforcement (M7-style, operator position).
- Lemma 5 is the formal content of closure (M14-style).

The remaining M-laws require resolving at least one of the explicit gaps G1–G3 (orientation, transport, neighborhood closure).

---

## 5) Next lemma targets (what to prove once gaps close)

Once G1–G3 are fixed with explicit definitions, the next “entry proofs” to add are:

1. A lemma that constructs `orientation` from the geometry of `Aα` (closes G1 → supports M5-type claims).
2. A lemma that proves a transport composition/propagation identity (closes G2 → supports M8-type claims).
3. A lemma showing `csi(α)` is induced by admissibility overlap or equivalent operational rule (closes G3 → supports M10-type closure).

