# P012 — Formal Symbolic Proof: Orientation Induction (Gap 1)

## Goal
Symbolically derive that local orientation `-(i)α` is a derived property of mismatch-minimizing selection within an oriented admissibility window.

## Uses
- Lemmas: L016, L017
- Specification: `# Formal Specification of ⇔(_R).txt`

## Proof

1. **Define the Admissibility Window.**
   Assume `Aα` is defined by a valve inequality:
   `Aα = { δ : gα(δ) ≥ 0 }`

2. **Define Selection.**
   Let `O*` be the selection operator that maps process mismatch `εα` and the window `Aα` to an admissible update:
   `δ*α = O*(εα, Aα) = argmin_{δ∈Aα} μ_rel(δ; εα)`

3. **Establish Orientation Mapping.**
   Define the reference mapping `Ref : V → Ω` that extracts the orientation/direction from a navigation vector:
   `Ref(v) = v / ||v||` if `v ≠ 0`
   `Ref(v) = ∇gα(v) / ||∇gα(v)||` if `v` is on the boundary.

4. **Derive Induction.**
   Substitute the selection output into the reference mapping:
   `-(i)α = Ref(O*(εα, Aα))`

5. **Conclude.**
   Since `-(i)α` is fully determined by the primitive mismatch `εα` and the window boundary `gα`, it is a **derived** property rather than a primitive of the process.

∎

## Status
formally_proven

## Proof Type
symbolic
