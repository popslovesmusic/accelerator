# Ordered Account of the Mathematics (Unity / Foundational Entry)

**Scope:** `docs/theory/foundational/5_03_26 unity/math/` (this directory only)  
**Date:** 2026-05-07  
**Status:** ordered account / synthesis of existing sources (no new proofs)  

This document is an *ordered account* of the mathematics already present in this folder. It is written to preserve the folder’s “additive-only” workflow: it does not revise prior notes; it orders them.

## 1) Organizing object: the core update constraint (indexed form)

Across the sources, the organizing object is the residue-conditioned two-way constraint coupling an **existence / participation** condition to an **admissibility-filtered update rule**:

`Eα > 0  ⇔_R  x'α = xα + Π_Aα ( Σ_{β ∈ csi(α)} transport(ωα, ωβ) )`

Where (ordered by role in the expression):

1. `Eα > 0` is the non-null participation / activation condition for index `α`.  
2. `⇔_R` is the residue-indexed coupling gate: the constraint is evaluated under a residue context `R` (history matters for evaluation, not just annotation).  
3. `xα` and `x'α` are the pre- and post-continuation states.  
4. `Π_Aα` is the admissibility projection/filter that enforces `Aα` *before* the increment is applied.  
5. `Σ_{β ∈ csi(α)} (…)` is the aggregate coupling contribution sourced from a neighborhood of indices `β`.  
6. `transport(ωα, ωβ)` (also written `Nav_T(ωα, ωβ)` in some sources) is the per-neighbor contribution.

Source alignment:
- `(ℰ ≠ 0) ⇔ δ_a(ℰ > 0).txt` introduces the three-region “existence / coupling / process” partition and an M-law list tied to those regions.
- `TN_MLaw_Derivation_v01.extracted.txt` treats the indexed expression above as canonical and argues it is generative for the M-law list, up to three explicit gaps.
- `00_series_alignment.md` unifies the notational variants and dependency ordering.

## 2) Minimal operator roles (what each symbol *does*)

The entry system in this directory pushes an operator-first reading: each object is introduced primarily by its operational role.

### 2.1 Existence / participation scalar (`Eα`, `ℰ`)

- Role: a scalar used to partition “non-null participation” (`Eα > 0`) from boundary regimes (including the “boundary-not-void” reading).
- Entry-level commitments: `Eα > 0` functions as the left-hand condition in the residue-coupled constraint; it is not treated as a stand-alone ontological claim inside this folder.

### 2.2 Residue (`R`) and residue-conditioned evaluation

- Role: residue is the state variable that gates evaluation of the two-way constraint, and is treated as the source of history dependence / persistence constraints.
- Entry-level commitment: derived statements must be residue-context consistent (formalized as Lemma `L005`).

`# Formal Specification of (R).txt` sharpens `R` itself: residue is not merely memory, substance, energy, or information alone. It is the accumulated structural consequence of continuation: retained interaction history, constraint accumulation, stabilization trace, admissibility deformation, and persistence influence.

The accepted review patch further qualifies what is and is not specified yet:

- Core: `R` is the persistent relational consequence of continuation.
- Typed form: `R_t ∈ ℛ` (a residue space).
- Open: the residue space `ℛ`, the update operator `Ψ`, and the reconciliation between compact and strong residue forms remain underspecified and are tracked as a highest-priority gap.

The (still generic) formal recurrence is:

`R_{t+1} = Ψ(R_t, x_t, x_{t+1})`

where `Ψ` is the residue update operator. Operationally, future continuation is therefore not memoryless:

`x_{t+1} = f(x_t, R_t)`

not solely `f(x_t)`. This gives residue the mathematical role of a non-Markovian constraint state: repeated continuation can deform admissibility geometry, and preserve orientation interaction effects in accumulated form.

The accepted patch upgrades the generic `Ψ` signature to explicitly include orientation and admissibility dependence:

`R_{t+1} = Ψ(R_t, x_t, x_{t+1}, ω_t, Π_A)`

Minimal requirements for any usable `Ψ` in this folder’s program:

1. history sensitivity
2. admissibility dependence
3. orientation dependence
4. nonzero-deviation sensitivity
5. explicit decay/saturation parameters if present

A candidate instantiation (still theoretical / not adopted as canonical here) is:

`R_{t+1} = λ R_t + η Π_{A_t}( NavT(ω_t, ω_{t+1}) )`

where `λ` controls persistence/decay and `η` controls inscription strength.

The same source gives two compact accumulation readings:

`R = ∫ δC`

and, in the stronger navigation-mediated form:

`R = Σ_k Π_A( NavT(ω_i, ω_j) )_k`

The accepted patch clarifies the relationship between these two forms:

- The strong summation form is a discrete candidate specification (one possible `Ψ`-realization), not an independent definition.
- The compact form is continuous shorthand; a proposed continuous limit is:
  - `R = ∫ Π_A( NavT(ω(s), ω(s+ds)) ) ds`

Finally, the patch corrects two over-strong residue claims into conditional statements:

- Stabilization: `ΔR > 0` may stabilize, destabilize, tighten, or block continuation depending on `Ψ` and `Π_A`.
- Zero-deviation: `ε = 0` implies no new inscription only if `Ψ` depends on nonzero deviation; decay toward `0` requires an explicit decay term (e.g. `0 ≤ λ < 1`).

`# Formal Specification of ⇔(_R).txt` sharpens this role: `⇔_R` is not ordinary logical equivalence and not identity. It is specified as a residue-mediated admissible transformation relation between distinguishable configurations. In compressed form:

`A ⇔_R B  ⇔  δ(A,B) > 0 and Π_A(R, ω_A, ω_B) = admissible`

This gives the connective four mathematical constraints:

1. **Non-equivalence:** `A ⇔_R B` does not imply `A = B` and does not reduce to `A iff B`.
2. **Distinction requirement:** `δ(A,B) > 0` is required; zero distinction collapses the continuation relation.
3. **Residue dependence:** different residue states can change the admissibility outcome, so the operator is history-sensitive and can support path dependence / hysteresis.
4. **Orientation dependence:** evaluation is relative to local orientation states `ω_A`, `ω_B`, later refined by the induced local reference `-(i)`.

The formal spec also provides an abstract type signature:

`⇔_R : (State_A, State_B, Residue, Orientation) -> Admissibility Relation`

or, more explicitly:

`⇔_R : (X × X × R × Ω) -> {admissible, unstable, forbidden}`

This strengthens the ordered reading of `L005`: closure is not a truth-table equivalence condition; it is residue-mediated admissible continuation under nonzero distinction.

### 2.3 Admissibility window (`Aα`) and projection (`Π_Aα`)

The admissibility note separates three distinct roles:

1. `Aα`: constraint domain (what is allowed).  
2. `Π_Aα`: filter/projection (removes inadmissible components; does not itself choose among admissible options).  
3. `O*`: selection inside the allowed domain (resolves ambiguity under mismatch).

Operator placement is mathematically decisive at entry level:
- Because the update is written as `x'α = xα + Π_Aα(…)`, admissibility is enforced *pre-update*.
- The entry lemmas isolate consequences that follow without committing to a mechanism class (ODE/PDE/CA/etc.).

### 2.4 Coupling neighborhood (`csi(α)`)

At entry level:
- `csi(α)` is treated as a typed index set for the RHS aggregate.
- The folder’s “gap list” requires closing a membership rule for `csi(α)` before stronger claims about coupling structure are promoted.

One candidate closure rule (stated in `TN_Admissibility_Window_and_Local_R.txt` and recorded as Lemma `L010`) is:

`β ∈ csi(α)  ⇔  Aα ∩ Aβ ≠ ∅` (evaluated under the current residue context).

This makes coupling *derived* from admissibility structure, rather than assumed as a fixed topology.

### 2.5 Transport (`transport(ωα, ωβ)` / `Nav_T(…)`)

At entry level:
- Transport is treated as a well-typed additive contribution that can be aggregated over `β ∈ csi(α)`.
- The folder explicitly marks the need for a transport structure strong enough to support “propagation” / composition identities (Gap 2; Lemmas `L008`–`L009`, Proof `P003`).

### 2.6 Local orientation / reference (`-(i)α`)

Across the folder, local orientation is *not* introduced as a primitive input; it is intended to be derived from admissibility + mismatch-minimizing selection:

- `TN_Admissibility_Window_and_Local_R.txt` states the role separation `Aα` vs `O*` vs `-(i)α`.
- `paper4_deriving_local_reference_minus_i_from_admissible_mismatch_minimizing_selection.md` gives an operator-family construction: admissible operator choice → induced reference.
- Proof `P002` packages a window-geometry + selection construction.
- Proof `P006` aligns `P002` to Paper 4’s operator-family presentation.

Within this folder’s proof plan, this is the core content of “closing Gap 1”.

## 3) Entry-level structural consequences (lemmas `L001`–`L005`)

The entry document `01_entry_lemmas_and_proofs.md` and Lemmas `L001`–`L005` isolate what follows from operator placement and intent, without committing to a particular mechanism class.

Ordered consequences:

1. **Admissible increment** (`L001`): if the update side is evaluated/active, then `Δxα := x'α − xα ∈ Aα`.  
2. **Empty-neighborhood fixed point** (`L002`): if `csi(α)=∅` and the update side is evaluated/active, then `x'α = xα`.  
3. **Boundary-not-void reading** (`L003`): “non-participating symmetry” is read as a degenerate fixed point (boundary condition), not an undefined state.  
4. **Pre-update constraint precedence** (`L004`): inadmissible components do not enter `Δxα` because filtering occurs prior to addition into state.  
5. **Residue-conditioned closure constraint** (`L005`): derived statements must preserve two-way coherence between the existence side and update side under the same residue evaluation context.

Proof packaging:
- `proofs/P001_entry_structural_consequences.md` packages `L001`–`L005` as a single theorem-level statement (explicitly conditional on the update-side being evaluated/active).

## 4) The M-law system as a consequence program

The working capture `(ℰ ≠ 0) ⇔ δ_a(ℰ > 0).txt` lists M0–M14 and groups them by “existence / coupling / process” regions.

`TN_MLaw_Derivation_v01.extracted.txt` formalizes a key internal program:
- The M-law list is not merely a summary; it is intended to be derivable from the core expression.
- The derivation is explicitly **theoretical** and explicitly calls out three missing definitional commitments.

The three gap obligations are consistent across:
- `00_series_alignment.md`
- `README.md`
- `TN_MLaw_Derivation_v01.extracted.txt`

Ordered gap list (with where this folder places the closures):

1. **Gap 1 (orientation from admissibility structure)**  
   - In this folder: Lemmas `L006`–`L007`, Proof `P002`, and Paper 4 alignment (`P006`).
2. **Gap 2 (transport structure sufficient for propagation identities)**  
   - In this folder: Lemmas `L008`–`L009`, Proof `P003`, and the “transport residual” observable `δ_T` used in Paper 4.
3. **Gap 3 (closed coupling-neighborhood membership rule)**  
   - In this folder: Lemmas `L010`–`L011`, Proof `P004`, and the admissibility-overlap rule in the admissibility note.

Gap packaging:
- `proofs/P005_gap_closure_to_closed_spec.md` records what becomes “closed up to implementation choice” once G1–G3 are supplied under a fixed residue evaluation context.

## 5) Extension notes: realizability, actualization, persistence (theory)

`# TN_Realizability_Actualization_an.txt` refines the interpretive layering around participation and history-gated continuation:

- Distinguishes four statuses: conceivable, realizable, actualized, persistent.
- Treats persistence as governed specifically by residue-conditioned coupling (the `⇔_R` role), not by distinguishability alone.
- Reinterprets “zero” as non-participation relative to a causal/admissibility window (not absolute absence).

This note is classified as theoretical and is not presented as simulation-validated inside this folder.

## 6) Proof governance as part of the mathematical system

This folder’s math is governed as an additive lemma/proof system:

- Lemma index: `REGISTRY_lemmas.md` (append-only list of `LNNN`).
- Proof index: `REGISTRY_proofs.md` (append-only list of `PNNN`).
- Planned proof path and gap dependencies: `PROOF_PLAN.md`.
- Workflow rule: `WORKFLOW_ADDITIVE_ONLY.md` (no edits; only additive supersession).

`governance_alignment_patchset_v_1.md` proposes additional governance structure (math object classes, proof classification, contradiction protocols, mapping taxonomy, lemma–simulation binding rules). This file is governance alignment, not a new mathematical claim.

## 7) Dependency-ordered reading path (within this folder)

For a reader who wants the mathematics in the most dependency-ordered sequence:

1. `README.md` and `00_series_alignment.md` (what the objects are, how the sources align).  
2. `# Formal Specification of (R).txt` (formalizes residue as accumulated continuation residue with update operator `Ψ`).  
3. `# Formal Specification of ⇔(_R).txt` (formalizes the connective as residue-mediated admissible transformation, not logical equivalence).  
4. `01_entry_lemmas_and_proofs.md` plus lemmas `L001`–`L005` (operator-first entry consequences).  
5. `proofs/P001_entry_structural_consequences.md` (the packaged entry theorem).  
6. `TN_MLaw_Derivation_v01.extracted.txt` (theoretical derivation program + explicit gaps).  
7. `TN_Admissibility_Window_and_Local_R.txt` (role separation: `Aα`, `Π_Aα`, `O*`, `-(i)α`; overlap-induced coupling).  
8. Gap closure scaffolds:
   - `proofs/P002_orientation_from_A_window.md` and `proofs/P006_paper4_alignment_for_minus_i.md` (Gap 1 program),
   - `proofs/P003_transport_propagation_identity.md` (Gap 2 program),
   - `proofs/P004_csi_closure_from_admissibility_overlap.md` (Gap 3 program),
   - `proofs/P005_gap_closure_to_closed_spec.md` (closure packaging).  
9. `paper4_deriving_local_reference_minus_i_from_admissible_mismatch_minimizing_selection.md` (operator-family derivation and observable layer; includes a minimal operational probe reference).  
10. `# TN_Realizability_Actualization_an.txt` (interpretive/theoretical refinements, explicitly non-empirical here).

## Appendix A) Concept nodes and relation edges (folder-local extraction)

This appendix is a folder-local concept extraction from the present sources (intended to support governed reasoning graph construction).

### A.1 Concept nodes (minimal)

- `C001`: existence_scalar (`Eα`, `ℰ`)  
- `C002`: residue (`R`)  
- `C003`: residue_conditioned_two_way_constraint (`⇔_R`)  
- `C004`: state (`xα`, `x'α`)  
- `C005`: admissibility_domain (`Aα`)  
- `C006`: admissibility_projection (`Π_Aα`)  
- `C007`: coupling_neighborhood (`csi(α)`)  
- `C008`: transport_operator (`transport` / `Nav_T`)  
- `C009`: mismatch (`εα`)  
- `C010`: mismatch_minimizing_selection (`O*`)  
- `C011`: induced_local_reference (`-(i)α`)  
- `C012`: transport_residual_observable (`δ_T`)  
- `C013`: admissibility_outcome (`admissible`, `unstable`, `forbidden`)  
- `C014`: residue_update_operator (`Ψ`)  

### A.2 Relation edges (each edge linked to a claim + evidence in-folder)

- `E001`: `C006` enforces `C005` pre-update  
  - `claim_id`: `CLM-L004`  
  - `evidence_id`: `EV-L004` (Lemma `L004_preupdate_constraint_precedence.md`)
- `E002`: `C003` forces residue-context coherence of derivations  
  - `claim_id`: `CLM-L005`  
  - `evidence_id`: `EV-L005` (Lemma `L005_residue_conditioned_closure.md`)
- `E003`: `C006( Σ C008 )` implies `Δxα ∈ C005`  
  - `claim_id`: `CLM-L001`  
  - `evidence_id`: `EV-L001` (Lemma `L001_admissible_increment.md`)
- `E004`: `csi(α)=∅` implies fixed point (conditional on update-side evaluated)  
  - `claim_id`: `CLM-L002`  
  - `evidence_id`: `EV-L002` (Lemma `L002_empty_neighborhood_fixed_point.md`)
- `E005`: `C010` + `C005` induce `C011` (conditional)  
  - `claim_id`: `CLM-P002`  
  - `evidence_id`: `EV-P002` (Proof `P002_orientation_from_A_window.md`)
- `E006`: overlap rule induces neighborhood membership (conditional)  
  - `claim_id`: `CLM-P004`  
  - `evidence_id`: `EV-P004` (Proof `P004_csi_closure_from_admissibility_overlap.md`)
- `E007`: `δ_T=0` is a sufficient propagation-consistency criterion (conditional on transport axioms)  
  - `claim_id`: `CLM-P003`  
  - `evidence_id`: `EV-P003` (Proof `P003_transport_propagation_identity.md`)
- `E008`: `C003` is residue-mediated admissible transformation, not logical equivalence or identity  
  - `claim_id`: `CLM-FORMAL-R-001`  
  - `evidence_id`: `EV-FORMAL-R-001` (`# Formal Specification of ⇔(_R).txt`)
- `E009`: `C003` maps state pairs, residue, and orientation to `C013`  
  - `claim_id`: `CLM-FORMAL-R-002`  
  - `evidence_id`: `EV-FORMAL-R-001` (`# Formal Specification of ⇔(_R).txt`)
- `E010`: `C002` updates by `C014(R_t, x_t, x_{t+1})`  
  - `claim_id`: `CLM-FORMAL-RESIDUE-001`  
  - `evidence_id`: `EV-FORMAL-RESIDUE-001` (`# Formal Specification of (R).txt`)
- `E011`: admissible navigation contributions accumulate into `C002` over continuation  
  - `claim_id`: `CLM-FORMAL-RESIDUE-002`  
  - `evidence_id`: `EV-FORMAL-RESIDUE-001` (`# Formal Specification of (R).txt`)

### A.3 Claim status discipline (folder-local)

All lemma/proof claims in this appendix are treated as:
- **theoretical / conditional**, because they depend on declared assumptions and/or explicit gap closures, and
- mechanism-independent at entry level unless a specific mechanism class is introduced (not done inside this folder’s entry lemmas).
