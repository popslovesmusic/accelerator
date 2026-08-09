# RT Calculus Note 043: Fixed-Point Uniqueness Conditions

**Patch ID:** `PATCH_PI_RT_CALCULUS_043`  
**Campaign ID:** `RT_CALCULUS_IMPLEMENTATION_001`  
**Depends On:** `PATCH_PI_RT_CALCULUS_042`  
**Status:** `APPLIED`

## Scope
This note records a bounded uniqueness classification for correct fixed points inside the existing continuation fixed-point scaffold. Source artifacts used: `docs/textbook/mono_process_textbook_complete.md` (the fixed-point uniqueness block and Appendix F glossary entries) and the user-provided patch proposal for `PATCH_PI_RT_CALCULUS_043`.

This is an additive documentation artifact. It does not edit any existing lemma or proof file in `theory/foundational/5_03_26 unity/math/`, and it does not alter `RT_core`.

## Directly Observed / Defined
- `UniqueFix(C)`: governed provisional reading of the uniqueness classification assigned to a correct fixed point within a bounded equivalence class.
- `EqClassFix(C)`: governed provisional reading of the equivalence class of fixed-point candidates under declared continuation, trace, and evaluation semantics.
- `FailUniqueFix(C)`: classified failure state produced when uniqueness verification fails.

$$ UniqueFix(C) := \text{uniqueness classification assigned to a correct fixed point within a bounded equivalence class} $$
$$ EqClassFix(C) := \text{equivalence class of fixed-point candidates under declared continuation, trace, and fixed-point evaluation semantics} $$
$$ FailUniqueFix(C) := \text{classified failure state when more than one non-equivalent correct fixed point exists in the bounded class} $$
$$ CorrectFix(C) \text{ is classified as } UniqueFix(C) \text{ only when every other correct fixed point in the same } ClassFix \text{ regime belongs to } EqClassFix(C) $$
$$ UniqueFix(C) \not\Rightarrow \text{universal fixed-point uniqueness} $$
$$ UniqueFix(C) \not\Rightarrow \text{universal fixed-point existence} $$
$$ UniqueFix(C) \not\Rightarrow \text{recovery} $$
$$ UniqueFix(C) \not\Rightarrow \sigma_{RT} $$
$$ UniqueFix(C) \not\Rightarrow RT_{core} \text{ change} $$

## Inferred Inside Framework
`PATCH_PI_RT_CALCULUS_042` defines the correctness layer for `CorrectFix(C)`. This note adds a separate uniqueness classification, so a correct fixed point can be evaluated for bounded equivalence-class isolation without promoting universal uniqueness or universal existence.

The uniqueness condition remains local to bounded evaluation and the declared continuation, trace, and fixed-point evaluation semantics. `FailUniqueFix(C)` records the classified fallback when more than one non-equivalent correct fixed point remains in scope, but it does not imply global rejection of fixed-point reasoning outside the declared regime.

## External Resemblance
This resembles quotient-class uniqueness criteria in other formal systems, but only as an analogy. It does not import external fixed-point theory, and it does not claim equivalence with any outside semantics.

## What It Does Not Prove
- It does not prove fixed-point uniqueness in the universal sense.
- It does not assert universal fixed-point existence.
- It does not introduce recovery.
- It does not introduce `\sigma_{RT}`.
- It does not alter `RT_core`.

## Failure Modes / Uncertainty
- The candidate may be correct but still fail isolation from non-equivalent correct fixed points.
- The candidate may exit the declared evaluation regime before uniqueness can be established.
- The declared equivalence semantics may be incomplete, which blocks uniqueness verification even if a witness seems available.
- `FailUniqueFix(C)` is diagnostic only; it does not settle any universal theorem.

## Status
- `claim_class`: `C1_DEFINED_PROVISIONAL`
- `evidence_class`: `C0`
- `governance_state`: `APPLIED`

## Governance Note
This addition is additive only. No existing lemma or proof file was edited. No local `GEMINI.md` applies to `docs/theory/foundational/5_03_26 unity/math/`; this note follows the higher-level repository instructions and the additive-only rule.
