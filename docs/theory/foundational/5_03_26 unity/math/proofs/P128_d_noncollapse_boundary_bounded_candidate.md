# Proof P128 — D Non-Collapse Boundary Bounded Candidate

## Goal

Provide an explicit, bounded derivation for `OBL-D-001E` under a declared finite threshold profile.

## Uses

- `L131` - Local D Evaluation and Projection Semantics
- `0012_epsilon_a_context_threshold_candidate.md`
- `0023_context_indexed_epsilon_semantics.md`
- `0030_d_kernel_internalization_bounded_rules.md`
- `0031_d_independent_adversarial_review_report.json`

## Statement

For a declared context profile `(A_C, epsilon_C)` and projected values `p,q`, assume:

```text
A_C is nonempty
epsilon_C > 0
p != q
distinction_C(p,q) >= epsilon_C
```

Then the bounded non-collapse predicate follows:

```text
NonCollapse_C(p,q)
```

## Derivation

1. The context profile is explicit input data; no global or silently inferred threshold is used.
2. Positivity of `epsilon_C` excludes the degenerate threshold.
3. Nonemptiness of `A_C` confirms that the profile has an admitted participant domain.
4. `p != q` excludes identity collapse.
5. The lower-bound premise supplies the threshold condition.
6. These four premises are exactly the conjuncts in the bounded `NonCollapse_C` rule, so conjunction introduction yields the conclusion.
7. The independent fixtures reject zero distinction, subthreshold distinction, and non-positive profiles.

## Scope boundary

This derives non-collapse only for the stipulated profile and projected pair. It does not derive `epsilon_C` for arbitrary domains, prove a universal threshold law, or establish preservation, injectivity, reversibility, or physical validity.

## Status

`restricted_local_argument_only`

Human review status: `APPROVED_BOUNDED` under `D_HUMAN_REVIEW_APPROVAL_P127_P128_20260730_001`. `OBL-D-001E` is `DISCHARGED_BOUNDED`; the C1 ceiling and theorem-promotion block remain active.

## Falsification vectors

- A zero or non-positive threshold is admitted.
- A subthreshold or equal projected pair is admitted contrary to the declared relation.
- A context with no admitted participant is accepted.
- The threshold is silently inferred from the output rather than supplied by the context profile.
