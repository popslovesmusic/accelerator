# P006 — Paper4 Alignment for `-(i)` (Addendum to P002; conditional)

## Goal
Incorporate the construction in:

- `paper4_deriving_local_reference_minus_i_from_admissible_mismatch_minimizing_selection.md`

as an explicit **operator-family** instantiation of the more abstract "orientation-from-window selection" idea in `P002`.

This note does not replace `P002`; it provides a second (compatible) construction path that matches Paper 4's vocabulary:

- operator family `O = (L, Q)` (admissibility leg + orientation leg),
- admissibility precedence,
- mismatch-minimizing selection `O*`,
- induced local reference `-(i)` as `Ref(O* · ε)` (not the operator itself),
- set-valued behavior under degeneracy.

## Uses
- Proofs: `P002` (as the abstract construction pattern)
- Lemmas: `L004`, `L005`
- Source manuscript: `paper4_deriving_local_reference_minus_i_from_admissible_mismatch_minimizing_selection.md`

## Proof

### D10 (Operator family)
Let `O = (L, Q)` where:

- `L` ranges over admissibility operators (Paper 4 uses `L ∈ {+, -}`),
- `Q` ranges over orientation operators (Paper 4 uses a minimal set such as `{++, +-, -+, --}`),
- admissibility precedence is enforced: admissibility is applied before orientation.

### D11 (Admissible operator set)
At each locus `(x,t)` (or for each index `α` under a residue evaluation context), let `O_adm(x,t)` be the set of operators `O` that satisfy the admissibility skeleton constraints (precedence + any compatibility rules imposed at that locus).

### D12 (Mismatch cost functional over operators)
Let `μ_rel(O; ε(x,t))` be a relational mismatch cost for applying operator `O` to mismatch state `ε` at that locus.

This is intentionally operational: the proof requires only that `μ_rel` induces an ordering over admissible operators.

### D13 (Mismatch-minimizing operator selection)
Define the minimizing operator set:

`O*(x,t) ∈ argmin_{O ∈ O_adm(x,t)} μ_rel(O; ε(x,t))`.

Allow `O*` to be set-valued when the minimizer is non-unique (degeneracy).

### D14 (Induced local reference)
Define the local reference/orientation object as:

`-(i)(x,t) := Ref( O*(x,t) · ε(x,t) )`,

where `Ref(·)` is a reference extraction mapping and `·` denotes the action of the selected operator on mismatch (as in Paper 4's `Ref(O* · ε)` phrasing).

Crucially: `-(i)` is the **induced reference**, not the operator `O*` itself.

---

### Proposition (Paper 4 construction is a valid induced-reference derivation; conditional)
Under D10–D14, `-(i)` is derived from:

1) admissibility constraints (through `O_adm`), and
2) mismatch-minimizing selection (through `argmin μ_rel`),

and therefore is not introduced as a new primitive object.

#### Proof
By D13, `O*` is selected from the admissible operator set by mismatch minimization; by D14, `-(i)` is a function only of `(O*, ε)` via `Ref`.

Because admissibility constraints are applied first (D10–D11), the construction respects admissibility precedence, matching the "pre-update constraint precedence" safeguard formalized structurally in Lemma `L004`.

Finally, because the framework treats the core constraint as residue-conditioned and closure-intended, any use of the derived `-(i)` in downstream update statements must remain coherent with the existence side under the same residue evaluation context (Lemma `L005`). ∎

---

### Compatibility note (P002 vs Paper 4)
`P002` was written in a "window geometry + selection" form (selection over admissible increments `δ ∈ Aα`).
Paper 4 is written in an "operator family + selection" form (selection over `O ∈ O_adm`).

These are compatible when an operator application produces a candidate increment and admissibility is enforced before update:

- `δ`-selection view: pick `δ* ∈ argmin_{δ ∈ A} μ_rel(δ; ε)` and set `-(i) := Ref(δ*)`.
- `O`-selection view: pick `O* ∈ argmin_{O ∈ O_adm} μ_rel(O; ε)` and set `-(i) := Ref(O* · ε)`.

In either case, `-(i)` is induced by mismatch-minimizing selection constrained by admissibility, and can be set-valued under degeneracy.

## Status
draft

