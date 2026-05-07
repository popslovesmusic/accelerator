# L012 — Compact–Strong Residue Equivalence (Gap target; open)

## Statement
Define the compact residue form:

`R = ∫ δC`

and the strong (discrete) candidate form:

`R = Σ_k Π_{A_k}( NavT(ω_k, ω_{k+1}) )`.

This lemma’s goal is to *prove or define* a precise relation between these forms (e.g., as a discrete specification of a residue update operator `Ψ` whose continuous limit yields the compact form), under an explicit choice of:

- residue space `ℛ` (typed form `R_t ∈ ℛ`),
- residue update operator `Ψ`,
- admissibility projection family `Π_A`,
- and a transport/navigation operator `NavT`.

## Dependencies
- Sources:
  - `# Formal Specification of (R).txt` (introduces `R_{t+1}=Ψ(...)` and the compact/strong forms)
  - `02_ordered_account_of_mathematics.md` (records the accepted review patch constraints and reconciliation)
- Assumptions (to be declared when this lemma is closed):
  - Well-typedness of `R` and all operator outputs in `ℛ`
  - A specific discretization scheme linking `δC` to admissible navigation increments

## Proof sketch
Open / not yet specified. This lemma is intentionally a gap target: the proof requires an explicit choice of `ℛ` and a concrete `Ψ` (or an equivalent accumulation rule) to make the compact integral and discrete sum comparable.

## Status
draft

## Supersedes / Superseded-by

