# P003 — Transport Identity / Propagation Law (closes G2, conditional)

## Goal
Given an explicit definition of the transport operator `transport(·,·)` (or `Nav_T(·,·)`), prove a minimal **compositional / frame-consistency identity** that justifies a "propagation" statement without committing to a particular mechanism class (ODE/PDE/CA/etc.).

This proof is **conditional**: it depends on transport axioms (D15–D18) that must be supplied by a concrete transport definition.

## Uses
- Lemmas: `L001`, `L004`, `L005`
- Entry definitions/assumptions: as stated in `01_entry_lemmas_and_proofs.md` (D1–D5, A1–A3)
- New definitions/assumptions (local to this proof): D15–D19, A8–A10

## Proof

### D15 (Reference-bearing state)
Assume each process index `α` has an associated reference-bearing state `ωα` (or derived reference `-(i)α` once `P002`/Paper 4-style construction is adopted). Transport is defined between such reference-bearing states.

### D16 (Transport contribution)
Assume `transport(ωα, ωβ)` is a well-typed element of the same increment space filtered by `Π_Aα`, so that the update-side sum is meaningful:

`Σ_{β ∈ csi(α)} transport(ωα, ωβ)`.

### D17 (Transport composition)
Assume transport supports a compositional identity along a chain of indices `(α, β, γ)` in the following sense:

There exists a composition operator `∘` (on transport contributions or their induced actions) such that:

`transport(ωα, ωγ) = transport(ωα, ωβ) ∘ transport(ωβ, ωγ)`

whenever the chain is "admissible for composition" under the residue context (i.e., the objects exist and the composition is defined).

This is the minimal algebraic content needed to speak about propagation across intermediates.

### D18 (Identity / null-transport element)
Assume there exists a neutral element `e` such that:

`transport(ωα, ωα) = e`

and `e` behaves as an identity under `∘`.

### D19 (Transport residual observable)
Define a transport residual observable `δ_T(α,β,γ)` measuring failure of composition:

`δ_T(α,β,γ) := dist( transport(ωα, ωγ), transport(ωα, ωβ) ∘ transport(ωβ, ωγ) )`,

where `dist(·,·)` is any nonnegative discrepancy functional with `dist(u,u)=0`.

---

### A8 (Composition respects admissibility filtering)
Assume admissibility filtering is applied pre-update (Lemma `L004`), and that the composed transport contribution is filtered by `Π_Aα` before entering the state update.

### A9 (Residue context fixed)
All equalities/inequalities in this proof are evaluated under a fixed residue evaluation context, so that the `⇔_residue` closure constraint is meaningful (Lemma `L005`).

### A10 (Non-degenerate composition regime)
Assume the composition regime excludes undefined composition cases (i.e., the chain is within the domain where `∘` and `dist` are defined).

---

### Theorem (Propagation identity; conditional)
Under D15–D19 and A8–A10, if `δ_T(α,β,γ)=0` then transport from `γ` to `α` is consistent with transport propagation through `β`:

`transport(ωα, ωγ) = transport(ωα, ωβ) ∘ transport(ωβ, ωγ)`.

Moreover, if `δ_T` is identically zero across all admissible triples in a neighborhood chain, then transport is path-consistent in that regime (propagation can be read as composition along the chain).

#### Proof
By definition D19, `δ_T(α,β,γ)=0` implies the two arguments of `dist` are equal, hence:

`transport(ωα, ωγ) = transport(ωα, ωβ) ∘ transport(ωβ, ωγ)`.

If this holds for every triple along a chain, repeated substitution yields consistency of transport across multi-hop propagation (associativity-like behavior is absorbed into the chosen `∘` and admissibility of composition). ∎

---

### Closure note (why this matters for the core biconditional)
The update-side rule uses admissibility-filtered sums of transport contributions. Lemma `L001` + Lemma `L004` ensure the applied increment is admissible and pre-filtered. This proof supplies the missing structural obligation for "propagation" readings: transport must be compositional (or have small residual `δ_T`) in a residue-consistent regime (Lemma `L005`).

Without an explicit `transport` definition satisfying D17–D19, any propagation statement remains a proposal rather than a derived identity.

## Status
draft

