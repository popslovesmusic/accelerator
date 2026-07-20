# MPF Closure Pilot — Formalization Gap Taxonomy & Promotion Ledger

**Promotion Packet ID**: `PROMOTION_RT_2026_07_20_LEAN_PILOT_OPTION_C`  
**Promotion Addendum ID**: `PROMOTION_RT_2026_07_20_LEAN_PILOT_OPTION_C_ADDENDUM`  
**Classification**: `PROVISIONAL_PROMOTION`  
**Authority Level**: `L1_FORMALIZED_PILOT`  
**Scope**: Lean 4 Proof Package (`proofs/lean/MpfClosurePilot.lean`)  
**Status**: FULLY VERIFIED (0 `sorry` warnings; Status Label: `fully_verified`, 15 proved theorems; legacy P111 string model pruned)  
**Compliance**: Non-Occlusive Humility Clause (MPF-CODEX-001)

---

## Standing Policy: Real Work or Pruned

### Governing Principle
All aspects, operators, or conditions in the formalization must do real work — i.e. the theorem attached to them must be capable of being **FALSE** under some other reasonable definition of its inputs — or they should be pruned outright rather than kept as decorative/placeholder content with a verified-sounding label.

### Test for Real Work
For any theorem $T$, ask: *is there a plausible alternate definition of the objects $T$ references under which $T$ would fail to typecheck or fail to hold?*
- If **NO** — if $T$ holds automatically for any total/well-typed definition of its inputs — $T$ does no independent work and should be pruned or explicitly marked as a non-claim (e.g. a totality/sanity check, not a verification).

### Standing Applicability
This rule governs all future additions to `MpfClosurePilot.lean` and any successor pilot files.

### Fork Resolution Record: Context-Gated Tensor Operator ($\otimes$)
The coupling projection operator $\otimes$ (`tensor`) was rebuilt to be Context-gated (`tensor (c : Context) (A B : Projection) : Projection`). When `ProjectionClosed c` holds, `tensor c A B` resolves to window intersection `proj_inter A B`. When $c$ is unclosed, `tensor c A B` resolves to `empty_projection` (window := fun _ => False).
- *Fork Selection*: The degenerate-value option was selected by default for structural consistency with the `valuation` / `Fails` boundary pattern in `MpfClosurePilot.lean`. This default choice is open to future revision.

---

## Executive Summary

A bounded pilot fragment of the **Mono-Process Framework** has been successfully mechanized and promoted to **Level L1 Formalized Pilot** status (`PROMOTION_RT_2026_07_20_LEAN_PILOT_OPTION_C` with Addendum `PROMOTION_RT_2026_07_20_LEAN_PILOT_OPTION_C_ADDENDUM`).

Within the explicit definitions encoded in `MpfClosurePilot.lean`, **fifteen theorems** have been machine verified without admitted proofs (`sorry`), demonstrating internal derivability and logical consistency of the encoded fragment relative to its formal definitions.

- **Verified Compiler Status**: Lean 4 compiler run (`lake build`) exit code 0, 0 warnings, 0 unexpected errors, `status_label: fully_verified`.
- **Promoted Scope**: Syntax closure (L116), Semantic closure & failure boundary (L117), Orientation frame alignment & collapse boundary (Option B), Relational model class satisfiability & countermodel failure (Option C), Process step deduction & invariant conservation (Option A), Projection signature preservation (P110), rebuilt Affect|Effect inheritance (P111), and Context-gated operator algebra (L118, P112). The legacy P111 string-pair label mapping remains pruned per Standing Policy.

---

## Revised Promoted Claim & Formal Progression Pathway

### Revised Promoted Claim (Level L1 Formalized Pilot)
> "A bounded pilot fragment of the Mono-Process Framework has been mechanized in Lean 4. Within the explicitly encoded definitions of this pilot, fifteen theorems have been machine verified without admitted proofs (`sorry`). This establishes internal derivability and logical consistency for the implemented pilot fragment relative to its formal definitions."

### Claim-Humility Principle
> "Machine verification demonstrates that the stated conclusions follow from the encoded definitions. It does not establish that those definitions are unique, complete, or representative of external reality."

### Multi-Level Formal Progression Pathway
- **Level L1 (Formalized Pilot)**: Single implementation successfully mechanized and machine verified. *(Achieved)*
- **Level L2 (Independent Formal Reproduction)**: Independent parties reproduce the mechanized results from the published specification. *(Next Target)*
- **Level L3 (Formal Generalization)**: Core theorems remain valid across generalized model classes rather than a single canonical implementation.
- **Level L4 (Empirical Correspondence)**: Where applicable, formal constructs demonstrate measurable correspondence with independently observed phenomena.

---

## Detailed Theorem Verification & Regression Ledger

| Theorem ID | Name / Purpose | Substance Class | Lean Proof Mechanism | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `L116_syntax_closure` | structural | Structural pattern match over 6 constructors | **VERIFIED (`rfl`)** |
| - | `L116_state_class` .. `L116_projection_class` | regression guard | Total pattern match check | **SANITY CHECK (Non-Claim)** |
| 2 | `L117_boundary_condition` | substantive | Independent `Fails`/`valuation` boundary collapse | **VERIFIED (Substantive, No sorry)** |
| 3 | `orientation_failure_boundary` | substantive | Misaligned frame collapse to `Value.zero_state` | **VERIFIED (Substantive, No sorry)** |
| 4 | `core_expression_satisfiability` | substantive | Canonical model `standard_model` satisfaction | **VERIFIED (Substantive, No sorry)** |
| 5 | `countermodel_boundary_failure` | substantive | Countermodel `unconditioned_model` failure | **VERIFIED (Substantive, No sorry)** |
| 6 | `step_admissibility_preservation` | substantive | Floor non-degeneration ($c_2.\text{adm\_floor} \ge c_1.\text{adm\_floor}$) | **VERIFIED (Substantive, No sorry)** |
| 7 | `step_residue_accumulation` | substantive | Monotonic trace accumulation ($r_2.\text{trace} \ge r_1.\text{trace}$) | **VERIFIED (Substantive, No sorry)** |
| 8 | `step_valuation_soundness` | substantive | Valid step valuation to `Value.valid_distinction` | **VERIFIED (Substantive, No sorry)** |
| 9 | `step_orientation_alignment_preservation` | substantive | Step alignment preservation ($c_2.\text{orientation.aligned} = \text{true}$) | **VERIFIED (Substantive, No sorry)** |
| 10 | `P110_projection_signature` | substantive | Non-zero valuation for admissible state terms | **VERIFIED (Substantive, No sorry)** |
| 11 | `P111_affect_effect_inheritance` | substantive | Non-failing terms produce valuation-linked `AEInheritance` | **VERIFIED (Substantive, no string labels)** |
| 12 | `P111_inheritance_boundary` | substantive | Failed terms collapse AE inheritance to `none` via L117 | **VERIFIED (Substantive boundary check)** |
| 13 | `L118_operator_algebra` | substantive | Conditional Context-gated $\otimes$ operator algebra | **VERIFIED (Substantive, `if_pos h_closed`)** |
| 14 | `P112_projection_intersection_specialization` | substantive | Conditional Context-gated $\Pi_A \otimes \Pi_B = \Pi_{A \cap B}$ via `L118_operator_algebra` | **VERIFIED (Substantive, delegates to L118)** |
| 15 | `tensor_unclosed_boundary` | substantive | Falsifiability check (unclosed context yields `empty_projection`) | **VERIFIED (Substantive, `if_neg h_not`)** |

### Pruned Legacy Model

The prior P111 implementation (`term_ae_inheritance`, `AffectComponent`, `EffectComponent`, and `AEPair` as string-label metadata) remains pruned. P111 is now represented only by valuation-linked `AEInheritance` and its failure boundary theorem.

---

## Governance & Standard Vocabulary

- **Recommended Language**: `machine verified`, `mechanized`, `formalized pilot`, `implemented fragment`, `relative to the encoded definitions`, `bounded scope`, `current formalization`, `provisional research framework`.
- **Prohibited Language**: `proved the framework`, `proved the theory`, `verified reality`, `mathematically complete`, `settled the mathematics`, `established physics`.
- **Next Milestone**: `L2_INDEPENDENT_FORMAL_REPRODUCTION` (requires independent Lean compilation pass and independent definition review).
