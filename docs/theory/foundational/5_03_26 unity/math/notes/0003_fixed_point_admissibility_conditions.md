# RT Calculus Note 041: Fixed-Point Admissibility Conditions

**Patch ID:** `PATCH_PI_RT_CALCULUS_041`  
**Campaign ID:** `RT_CALCULUS_IMPLEMENTATION_001`  
**Depends On:** `PATCH_PI_RT_CALCULUS_040`  
**Status:** `APPLIED`

## Scope
This note records a bounded acceptance layer for fixed-point candidates inside the existing continuation fixed-point scaffold. Source artifacts used: `textbook/mono_process_textbook_complete.md` (the fixed-point semantics block and Appendix F fixed-point glossary entries) and the user-provided patch proposal for `PATCH_PI_RT_CALCULUS_041`.

This is an additive documentation artifact. It does not edit any existing lemma or proof file in `theory/foundational/5_03_26 unity/math/`, and it does not alter `RT_core`.

## Directly Observed / Defined
- `AdmFix(C)`: governed provisional reading of admissible fixed-point semantics for candidate `C`.
- `Bound\Phi(C)`: declared finite evaluation boundary for `Eval\Phi(C)`.
- `Inv\Phi(C)`: continuation-invariance condition under further declared applications of `\Phi` within the bounded evaluation regime.
- `FailAdmFix(C)`: classified failure state produced when a candidate does not satisfy the fixed-point admissibility conditions.

$$ AdmFix(C) := \text{admissible fixed-point semantics for } CandFix(C) \text{ under the declared bounded regime} $$
$$ Bound\Phi(C) := \text{declared finite evaluation boundary for } Eval\Phi(C) $$
$$ Inv\Phi(C) := \text{condition that further declared applications of } \Phi \text{ do not change the resulting continuation condition within } Bound\Phi(C) $$
$$ FailAdmFix(C) := \text{classified failure state when } CandFix(C) \text{ does not satisfy the admissibility conditions} $$
$$ CandFix(C) \text{ is admissible as } AdmFix(C) \text{ only when } C \in ClassFix, \Phi(C) \text{ is declared, } Eval\Phi(C) \text{ is bounded by } Bound\Phi(C), \text{ and } Eval\Phi(C) \text{ yields } Fix(C), \text{ and } Fix(C) \text{ satisfies } Inv\Phi(C) $$
$$ FailAdmFix(C) \not\Rightarrow \text{fixed-point correctness} $$
$$ FailAdmFix(C) \not\Rightarrow \text{fixed-point uniqueness} $$
$$ FailAdmFix(C) \not\Rightarrow \text{universal fixed-point existence} $$
$$ FailAdmFix(C) \not\Rightarrow \text{recovery} $$
$$ FailAdmFix(C) \not\Rightarrow \sigma_{RT} $$
$$ FailAdmFix(C) \not\Rightarrow RT_{core} \text{ change} $$

## Inferred Inside Framework
`PATCH_PI_RT_CALCULUS_040` defines the candidate semantics layer for `CandFix(C)` and `Fix(C)`. This note adds a separate admissibility gate, so a candidate can be boundedly evaluable without automatically being accepted as admissible fixed-point semantics.

The gate remains local to the typed class, declared operator, finite evaluation boundary, and invariance condition. `FailAdmFix(C)` records a classified fallback when any declared condition is missing or violated, but it does not imply global rejection of fixed-point reasoning outside the declared scope.

## External Resemblance
This resembles typed proof obligations or admissibility checks in other formal systems, but only as an analogy. It does not import external fixed-point theory, and it does not claim equivalence with any outside semantics.

## What It Does Not Prove
- It does not prove fixed-point correctness.
- It does not prove fixed-point uniqueness.
- It does not assert universal fixed-point existence.
- It does not introduce recovery.
- It does not introduce `\sigma_{RT}`.
- It does not alter `RT_core`.

## Failure Modes / Uncertainty
- The candidate may be well-formed but still exceed the declared boundary.
- The candidate may yield a stable-looking state while failing the typed admissibility gate.
- The declared operator may be missing, which blocks admissibility even if a witness seems available.
- `FailAdmFix(C)` is diagnostic only; it does not settle any universal theorem.

## Status
- `claim_class`: `C1_DEFINED_PROVISIONAL`
- `evidence_class`: `C0`
- `governance_state`: `PROPOSED`

## Governance Note
This addition is additive only. No existing lemma or proof file was edited. No local `GEMINI.md` applies to `docs/theory/foundational/5_03_26 unity/math/`; this note follows `WORKFLOW_ADDITIVE_ONLY.md` and the higher-level repository instructions.
