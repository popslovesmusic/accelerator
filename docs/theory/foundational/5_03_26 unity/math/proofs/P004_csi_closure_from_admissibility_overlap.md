# P004 — Neighborhood Closure from Admissibility Overlap (closes G3, conditional)

## Goal
Assuming a closed membership rule for the coupling neighborhood `csi(α)` (aka `CSI(α)`), show that:

1) coupling membership is **dynamically induced** by admissibility structure (not a primitive fixed topology), and
2) the resulting neighborhood rule is compatible with residue-conditioned closure (the `⇔_residue` constraint).

This proof is **conditional**: it requires an explicit admissibility-window definition `Aα` and a specific overlap-based closure rule.

## Uses
- Lemmas: `L002`, `L004`, `L005`
- Source note support: `TN_Admissibility_Window_and_Local_R.txt` (overlap rule proposal)

## Proof

### D20 (Residue-conditioned admissibility windows)
Assume each process index `α` has an admissibility window `Aα` that depends on local mismatch/capacity/history (shorthand):

`Aα = A(εα, ρα, Rα)`,

where `Rα` is the local residue/history state participating in the `⇔_residue` evaluation context.

This captures the intended meaning that admissibility is local and history-gated.

### D21 (Overlap-based neighborhood closure rule)
Define neighborhood membership by mutual admissibility overlap under the same residue evaluation context:

`β ∈ csi(α)  ⇔  Aα ∩ Aβ ≠ ∅`  (evaluated under the current residue context).

This is the candidate closure rule proposed in the admissibility-window note and the derivation note’s gap list.

### D22 (Symmetry of membership)
From D21, membership is symmetric in the sense:

`β ∈ csi(α) ⇔ α ∈ csi(β)`,

because `Aα ∩ Aβ ≠ ∅` is symmetric under swapping `α,β`.

---

### Proposition 1 (Neighborhood is induced; not primitive)
Under D20–D22, `csi(α)` is not a primitive object: it is induced by the admissibility windows, hence by `(ε, ρ, R)` through `A(·)`.

#### Proof
By D21, membership is defined entirely in terms of `Aα` and `Aβ`. By D20, each `Aα` is determined by local state variables `(εα, ρα, Rα)` under the current residue context. Therefore `csi(α)` is induced by those quantities and can change as they change. ∎

### Proposition 2 (Empty neighborhood corresponds to disjoint windows)
For any `α`, `csi(α)=∅` if and only if `Aα` has empty overlap with every `Aβ` (for `β` in the candidate index set under consideration).

#### Proof
Immediate from D21 by definition of set membership. ∎

### Proposition 3 (Compatibility with fixed-point boundary under no overlap)
If `csi(α)=∅` and the update side is evaluated/active for `α`, then `x'α=xα` (fixed point), consistent with the reading that “no coupling” is a boundary condition rather than undefined.

#### Proof
This is Lemma `L002`. The role of D21 is interpretive: it supplies a concrete reason for `csi(α)=∅` (no admissibility overlap), but the fixed-point conclusion follows from the update structure once emptiness holds. ∎

### Proposition 4 (Residue-conditioned closure compatibility)
Under D20–D21, the neighborhood rule is residue-consistent: changes in residue can change `Aα` and thus change `csi(α)`, but any claim that uses neighborhood membership must be evaluated under the same residue context as the biconditional.

#### Proof
By D20, `Aα` depends on residue. By D21, `csi(α)` depends on `Aα`. Therefore membership is residue-dependent. Lemma `L005` requires that derived statements preserve the two-way residue-conditioned closure constraint under a fixed residue evaluation context; hence the neighborhood rule must be applied under that same context. ∎

---

## Status
draft

