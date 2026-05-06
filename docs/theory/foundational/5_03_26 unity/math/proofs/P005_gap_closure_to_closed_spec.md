# P005 — From Gap Closures (G1–G3) to a Closed Core Specification (conditional)

## Goal
State precisely what becomes "closed" about the core residue-conditioned biconditional once the three explicit gap closures are supplied:

- **G1:** oriented admissibility window structure sufficient to derive local reference/orientation `-(i)`
- **G2:** explicit `transport(·,·)` definition sufficient for propagation identities
- **G3:** closed neighborhood membership rule for `csi(α)` / `CSI(α)` (candidate: admissibility overlap)

This proof is a **packaging theorem**: it does not add new primitives; it records the minimal closure consequences and the dependency ordering.

## Uses
- `P002` (orientation/reference derived from admissibility + mismatch selection) — closes G1 (conditional)
- `P003` (transport propagation identity via composition/residual) — closes G2 (conditional)
- `P004` (neighborhood closure via admissibility overlap) — closes G3 (conditional)
- Lemma `L005` (residue-conditioned closure constraint)

## Proof

### Theorem (Closed-spec consequence; conditional)
Assume the following three conditional constructions/axioms are in force under a fixed residue evaluation context:

1) **Orientation closure (G1):** the local reference/orientation object `-(i)α` is derived (not primitive) by the admissibility+selection construction of `P002` (or equivalently the Paper 4 operator-family instantiation).

2) **Transport closure (G2):** the transport operator satisfies a compositional/frame-consistency identity with a well-defined residual `δ_T` as in `P003`, so that "propagation" statements have a concrete identity criterion (`δ_T=0`).

3) **Neighborhood closure (G3):** coupling neighborhood membership is given by a closed rule such as admissibility overlap as in `P004`:
   `β ∈ csi(α) ⇔ Aα ∩ Aβ ≠ ∅` (evaluated under the residue context).

Then the core update-side expression

`x'α = xα + Π_Aα( Σ_{β ∈ csi(α)} transport(ωα, ωβ) )`

can be read as a **closed specification up to implementation choice** in the following sense:

- `csi(α)` is no longer an undeclared primitive: it is induced by admissibility (P004).
- `transport(·,·)` is no longer a black box for propagation claims: it is constrained by a stated identity/residual (P003).
- the local orientation/reference term needed for reference-mediated transport is no longer assumed: it is induced by admissible mismatch-minimizing selection (P002 / Paper4 alignment).

Moreover, by Lemma `L005`, any claim about the update-side behavior must remain coherent with the existence-side condition under the same residue evaluation context, so closure is **residue-consistent** by construction.

#### Proof
Items (1)–(3) are exactly the gap-closure assumptions. Each removes one explicit "undefined" component of the core expression's right-hand side:

- P004 supplies a definition of the index set `csi(α)`.
- P003 supplies the algebraic identity criterion that justifies propagation/composition readings of `transport`.
- P002 supplies a derivation of the local reference `-(i)α` needed when transport is expressed as reference-mediated.

Therefore, under these assumptions, the right-hand side is specified without leaving `csi`, `transport`, or `-(i)` as free primitives. Residue consistency follows from Lemma `L005`. ∎

### Dependency ordering note
The gap closures are partially ordered operationally:

- a usable neighborhood rule (G3) typically depends on having a concrete admissibility window definition (G1-side structure for `Aα`), and
- a transport propagation identity (G2) can be stated independently, but becomes interpretable as "reference-mediated transport" once the induced reference `-(i)` is available (G1).

## Status
draft

