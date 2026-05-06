# L008 — Transport Composition + Identity Scaffold (G2)

## Statement
Assume the transport operator `transport(·,·)` (aka `Nav_T(·,·)`) is defined between reference-bearing states (e.g., `ωα` or derived `-(i)α`) and that it supports:

1) an **identity** element for self-transport, and
2) a **composition** rule along chains.

Formally, assume there exists a composition operator `∘` such that for admissible triples `(α,β,γ)` under the current residue context:

- (Identity) `transport(ωα, ωα) = e` where `e` is neutral for `∘`
- (Chain composition) `transport(ωα, ωγ) = transport(ωα, ωβ) ∘ transport(ωβ, ωγ)`

Then the framework has the minimal algebraic structure needed to treat "propagation" as transport composition (G2 scaffold).

## Dependencies
- Source alignment:
  - `TN_MLaw_Derivation_v01.extracted.txt` (Gap 2: explicit `Nav_T` transport structure required for propagation statements)
  - `paper4_deriving_local_reference_minus_i_from_admissible_mismatch_minimizing_selection.md` (defines transport residual `δ_T` and uses reference-mediated transport observables)
- Assumptions:
  - A1 (Well-typedness)
  - A10-style: composition is defined for the chain in the current residue context
- Prior lemmas: none

## Proof sketch
This lemma is a scaffold: it records the minimal transport axioms required for propagation identities. No further derivation is possible until `transport` and `∘` are explicitly defined in a concrete model (graph/ODE/PDE/etc.). ∎

## Status
draft

## Supersedes / Superseded-by

