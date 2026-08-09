# P002 — Orientation-from-Window Construction (closes G1, conditional)

## Goal
Assuming an explicit **oriented structure** for the admissibility window `Aα`, construct a well-defined local orientation/reference object `orientation(α)` (shorthand: `-(i)α`) and prove it is **induced by selection under mismatch**, rather than introduced as a primitive.

This proof is **conditional**: it upgrades "orientation" from a placeholder to a derived object only under the specific structural assumptions listed below.

## Uses
- Lemmas: `L001`, `L004`, `L005`
- Definitions: `Aα`, `Π_Aα` (as in the entry doc)
- New definitions (local to this proof): D6–D9
- Assumptions: A1–A3 (entry) plus A4–A7 (below)

## Proof

### D6 (Window given by an oriented constraint function)
Assume `Aα` is specified by a scalar constraint function `gα` on candidate increments `δ` (in the same space used by the update increment), such that:

`Aα := { δ : gα(δ) ≥ 0 }`.

Assume `gα` is differentiable on the boundary `∂Aα := { δ : gα(δ) = 0 }`, and `∇gα(δ) ≠ 0` on `∂Aα`.

Interpretation: `∇gα` provides a **boundary normal**, hence an orientation for the window boundary.

### D7 (Mismatch objective / selection functional)
Let `μ_rel(·; εα)` be a mismatch objective functional defined on candidate increments, parameterized by the local mismatch/pressure `εα` (treated as given in the theoretical mapping).

### D8 (Selection operator inside the window)
Define the selection operator `O*α` to return at least one admissible minimizer:

`δ*α ∈ argmin_{δ ∈ Aα} μ_rel(δ; εα)`.

If the minimizer is not unique, treat `δ*α` as **set-valued** (degeneracy is allowed).

### D9 (Induced local reference / orientation)
Define the induced reference/orientation as a function of the selected admissible increment:

`-(i)α := Ref(δ*α)`,

where `Ref(·)` is a mapping that extracts the relevant orientation-bearing information from `δ*α` (e.g., a unit direction `δ*α/||δ*α||` when `δ*α ≠ 0`, or a boundary-normal direction when selection lands on `∂Aα`).

This definition is intentionally abstract: the proof only requires that `Ref` depends **only** on `δ*α` (and thus only on `Aα` and `μ_rel` via selection).

---

### A4 (Existence of minimizers)
Assume the minimizer set `argmin_{δ ∈ Aα} μ_rel(δ; εα)` is non-empty for the residue context in which the update is evaluated.

### A5 (Admissibility acts before update addition)
Assume the applied increment is admissibility-filtered before state update (entry assumption A2 / Lemma `L004`), i.e. the applied increment lies in `Aα`.

### A6 (Orientation is read from window geometry + selection output)
Assume that any local orientation object used by transport is determined by the selected admissible increment (via `Ref`), and not introduced independently.

### A7 (Residue context fixed)
All objects above are evaluated under a fixed residue evaluation context (so the `⇔_residue` closure constraint is well-posed).

---

### Theorem (Orientation is induced by window + mismatch selection; conditional)
Under D6–D9 and A4–A7, the orientation/reference object `-(i)α` is **not a primitive input**. It is induced by:

1) the admissibility window geometry (via `Aα`, and its oriented boundary through `∇gα`), and
2) mismatch-minimizing selection within that window (via `μ_rel` and `O*α`).

In particular, if admissibility filtering is enforced pre-update, then `-(i)α` depends only on objects already required to evaluate the update increment (admissibility + mismatch), and can therefore be treated as **derived** from the update structure rather than assumed.

#### Proof
By Lemma `L001` (and the update structure), the applied increment `Δxα` lies in `Aα`.
By Lemma `L004`, inadmissible components cannot enter the applied increment (admissibility precedence), so any increment used for downstream interpretation must be an element of `Aα`.

By D8 and A4, the selection operator returns at least one mismatch-minimizing admissible increment `δ*α ∈ Aα`.
By D9 and A6, the local reference/orientation `-(i)α` is defined purely as a function of this selected admissible increment.

Therefore `-(i)α` is induced by `(Aα, μ_rel, εα)` through the selection mapping, and is not an independent primitive.

Finally, by Lemma `L005`, any statement that uses `-(i)α` on the update side must remain consistent with the existence side under the same residue evaluation context, so the induced-reference reading is constrained to be residue-consistent (A7). ∎

## Status
draft

