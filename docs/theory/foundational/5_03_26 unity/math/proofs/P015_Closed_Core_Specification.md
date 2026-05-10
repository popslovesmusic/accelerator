# P015 — Closed Core Specification (v2)

## Goal
Consolidate the gap closures (G1–G3) into a single, formally closed specification of the core residue-conditioned biconditional.

## Uses
- Gap 1: P012 (Orientation Induction)
- Gap 2: P013 (Propagation Law)
- Gap 3: P014 (Neighborhood Closure)
- Lemmas: L022, L023, L024, L016, L017, L018, L019, L020, L021

## Proof

1. **State the Core Biconditional.**
   `ℰα > 0 ⇔_R x'α = xα + Π_Aα( Σ_{β∈csi(α)} NavT(ωα, ωβ) )`

2. **Closure of Interaction Domain (G3).**
   From P014, the neighborhood `csi(α)` is derived from admissibility window overlap:
   `csi(α) = { β : Aα ∩ Aβ ≠ ∅ }`
   This removes `csi` as a primitive topology.

3. **Closure of Orientation (G1).**
   From P012, the orientation `-(i)α` is derived from mismatch-minimizing selection within the oriented boundary of `Aα`:
   `-(i)α = Ref(O*(εα, Aα))`
   This removes `-(i)` as a primitive reference.

4. **Closure of Propagation (G2).**
   From P013, the transport operator `NavT` supports algebraic composition, ensuring that state continuations across the interaction domain are frame-consistent:
   `NavT(α, γ) = NavT(α, β) ∘ NavT(β, γ)`

5. **Consolidation.**
   The core expression is now **structurally closed**: all interaction and orientation components are derived from the process primitives (`ε, ρ, R`) and the geometry of the admissibility window `A`.

∎

## Status
formally_proven

## Proof Type
symbolic

## Supersedes / Superseded-by
Supersedes: P005
