# Candidate Contract: `epsilon_a,C` Context Threshold

## Status

`CANDIDATE_FORMAL_SPECIFICATION`  
Epistemic status: `CONJECTURED`  
Proof status: `OBLIGATIONS_IDENTIFIED`  
Obligation: `OBL-D-001B`

## Definition

For a declared context `C`, the admissibility floor is an explicit context-indexed field:

```text
epsilon_a,C := C.admissibility_rule.threshold
```

The threshold contract requires:

```text
epsilon_a,C in OrderedThreshold_C
epsilon_a,C > 0
```

`epsilon_a,C` is not a global constant, is not silently inferred from an output, and is not derived by `Eval_D,C` during evaluation. A context may derive its threshold upstream from a declared rule, but the resulting value must be materialized in `C` before `Eval_D,C` is invoked.

## Admissibility Rule

For a defined distinction value `D_C(x)`:

```text
Adm_D,C(x) iff Defined(Eval_D,C(x)) and D_C(x) > epsilon_a,C
```

If `C` lacks a positive threshold, the result is `UNDEFINED_INCOMPLETE_CONTEXT`; this is distinct from a typed input failing the threshold, which is `UNDEFINED_INADMISSIBLE` under the OBL-D-001A contract.

## Context Independence Boundary

Two contexts may use different thresholds. Reproducibility therefore requires the context identifier, threshold value, comparison rule, and threshold provenance to travel with each classification. A result classified under `C1` cannot be silently compared with a result classified under `C2` as though the thresholds were identical.

This contract does not establish threshold stability under perturbation, uniqueness of threshold derivation, or physical meaning. Those require the bounded sensitivity campaign and human review.

## Acceptance Tests

1. A complete context with a positive threshold classifies `D_C(x) > epsilon_a,C` deterministically.
2. A missing or non-positive threshold returns `UNDEFINED_INCOMPLETE_CONTEXT`.
3. A typed value at or below the declared threshold returns `UNDEFINED_INADMISSIBLE`.
4. Different context thresholds remain distinguishable in the recorded output.
5. No classification uses an implicit global threshold.

Until the sensitivity campaign and human review pass, `OBL-D-001B` remains `OPEN` and the threshold remains `C1_DEFINED_PROVISIONAL`.

