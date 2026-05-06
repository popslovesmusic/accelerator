# Unity / Math — Document Alignment Notes (2026-05-05)

This folder currently contains three related documents in the **Mono-Process Framework — Theoretical Foundations Series**:

- `(ℰ ≠ 0) ⇔ δ(ℰ  0).txt` — working capture of the **core biconditional** and a compact “M Law” list plus variable-role notes.
- `TN_MLaw_Derivation_v01.docx` (and `TN_MLaw_Derivation_v01.extracted.txt`) — derivation note arguing the **M-Laws are generable** from a single indexed update biconditional.
- `TN_Admissibility_Window_and_Local_R.txt` — companion note separating the roles of **admissibility window** `Aα`, **projection** `Π_Aα`, **selection** `O*`, and induced **local reference** `−(i)α`.

The goal of this file is to make the documents read as one coherent chain: *core expression → operator roles → M-law derivations → known gaps / obligations*.

---

## 1) Notation unification (minimal, non-breaking)

Across the three documents, the same objects appear under slightly different glyphs. For internal consistency, interpret:

- `Eα` and `ℰ` as the same scalar: **total deviation magnitude / existence scalar** for process `α`.
  - Use `Eα` when indexing matters; use `ℰ` when talking about the non-indexed regime.
- `δ(ℰ > 0)` in the working capture as shorthand for “the **process/update side** is active”.
  - In indexed form this can be read as the update increment:
    - `Δxα := x'α − xα = Π_Aα ( Σ_{β ∈ CSI(α)} Nav_T(ωα, ωβ) )`
- `ωα` as a **phase-like state descriptor** for `α` (input to transport).
- `−(i)α` as an **induced local reference/orientation** derived from selection under mismatch (not a primitive input).
  - When the admissibility note writes `Nav_T(−(i)α, −(i)β)`, read this as a refinement step: `ω` is being replaced by the derived reference variable once `O*` is defined.

This keeps all three documents consistent without rewriting any of them.

---

## 2) “Core expression” (single canonical reading)

Use this as the canonical core expression (matches `TN_MLaw_Derivation_v01`):

`Eα > 0  ⇔_R  x'α = xα + Π_Aα ( Σ_{β ∈ CSI(α)} Nav_T(ωα, ωβ) )`

Interpretation alignment:

- Left (`Eα > 0`): **existence / non-null participation** condition (working capture “Existence Region”).
- Connective (`⇔_R`): **residue-indexed coupling gate**; “biconditional” is *historically conditioned* by `R`.
- Right (update): **continuation step** = admissibility-filtered transport sourced over `CSI(α)` (working capture “Coupling + Process Regions”).

Key “read-it-both-ways” constraint:

- `M14 (Closure Rule)` is exactly the requirement that both directions are enforced under `R` (not “two implications that happen to be true”).

---

## 3) Role separation (resolving the main ambiguity)

`TN_Admissibility_Window_and_Local_R.txt` supplies the critical separation that prevents conflation:

- `Aα`: admissibility **domain** (what is allowed).
- `Π_Aα`: admissibility **projection/filter** (removes inadmissible components).
- `O*`: **selection** within the admissible domain (resolves ambiguity under mismatch).
- `−(i)α`: **induced local reference** produced by selection (the orientation that transport then uses).

One consistent integrated reading of the update step is:

1. Compute transport contributions over current couplings: `Σ_{β∈CSI(α)} Nav_T(ωα, ωβ)`.
2. Apply admissibility projection: `Π_Aα( … )` to enforce constraints *before* state update.
3. If selection is required (degeneracy / ambiguity), use `O*` to induce `−(i)α`, then re-express transport as reference-mediated: `Nav_T(−(i)α, −(i)β)`.

This is consistent with:
- the working capture’s “valve mechanism” language for admissibility, and
- the derivation note’s identification of “Gap 1–3” as required definitional commitments.

---

## 4) How the three docs depend on each other (dependency graph)

- `(ℰ ≠ 0) ⇔ δ(ℰ  0).txt`
  - provides: the three-region intuition + M0–M14 list + candidate valve sketch `A(ε,ρ,R)=σ(ρ+αR−βε−θ)`.
  - lacks: fully specified `Aα` orientation, `Nav_T` structure, and a closed `CSI(α)` rule.

- `TN_MLaw_Derivation_v01.docx`
  - provides: formal claim “M-laws are derivable”, plus the **three explicit gaps** that must be defined:
    - Gap 1: `Aα` orientation (binds to M5).
    - Gap 2: `Nav_T` transport structure (binds to M8).
    - Gap 3: `CSI(α)` formation rule (binds to M10).

- `TN_Admissibility_Window_and_Local_R.txt`
  - provides: role separation + a candidate `CSI` formation rule via admissibility overlap:
    - `β ∈ CSI(α) ⇔ Aα ∩ Aβ ≠ ∅`
  - therefore: directly supports closing **Gap 3**, and partially supports **Gap 1** by making `Aα` explicitly dynamic in `(εα, ρα, Rα)`.

Practical reading order:
1. Read `TN_MLaw_Derivation_v01` (what must be true if the core expression is taken seriously).
2. Read `TN_Admissibility_Window_and_Local_R` (how to define `Aα`, `Π_Aα`, `O*`, `−(i)` without conflation).
3. Re-read `(ℰ ≠ 0) ⇔ δ(ℰ  0).txt` and treat it as the “compressed working capture” that should be updated only when the three gaps are closed.

---

## 5) Current “known gaps” (cross-doc consistency checklist)

These are the exact items that currently prevent the set from being a single closed specification:

1. **`Aα` orientation / reference binding (M5)**:
   - need an explicit statement of what structure in `Aα` induces `−(i)α` (boundary, normal, inequality gradient, etc.).
2. **`Nav_T` transport structure (M8)**:
   - need an operational definition of what “transport” does and what the `T` index means (frames, parallel transport, residue connection, etc.).
3. **`CSI(α)` membership rule (M10 demanded)**:
   - `TN_Admissibility_Window_and_Local_R` proposes a clean closure via admissibility-overlap; the working capture and derivation note should converge on *one* rule statement.

Until these are specified, the safest internal status for all three documents is: **theoretical / draft**, with explicit “gap” markers (which `TN_MLaw_Derivation_v01` already does).

