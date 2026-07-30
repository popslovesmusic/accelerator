# Notebook 23 D/E Held-Out Stress — Run Analysis

## Scope

This report analyzes the supplied archive `MPF_SIM_D_E_HELD_OUT_STRESS_001_RESULTS.zip` against the frozen Notebook 23 specification. The archive contains 324 rows across contexts C4-C6, six declared cases, bare/enriched witness modes, three seeds, and two replay passes.

## Directly observed in the archive

- `row_count`: 324.
- `control_agreement_count`: 324; `control_mismatch_count`: 0.
- `replay_agreement_count`: 324; `replay_mismatch_count`: 0.
- `falsification_flag_count`: 0.
- `leakage_violation_count`: 0.
- Representability counts: `REPRESENTABLE` 108; `REJECT_CONTEXT` 54; `REJECT_HISTORY` 54; `REJECT_TYPE` 54; `REJECT_WITNESS` 54.
- Non-collapse counts: `NON_COLLAPSED` 216; `REJECT_PROFILE` 54; `REJECT_SUBTHRESHOLD` 54.
- The archive manifest, summary, falsification report, and embedded specification are present, and the ZIP passes integrity testing.

## Inferred inside the bounded framework

Within the declared finite grid, the supplied outputs are consistent with exact replay and the expected control matrix. The bounded conclusion recorded by the archive is support for replay consistency on these rows, with no flagged counterexample in this run.

## Integrity limitation

The archive manifest reports `spec_hash_check.matches: false`: its standard-canonical recomputation is `2b499fd09f71f315c371c14798e66c4eb44b683f1e7ddefc38e45d892a05f258`, while the declared frozen specification hash is `c8b796265606d70fe14c78a8989898a591d77d8361376d64b4ad82fd326426bd`. This prevents automatic elevation beyond archive provenance until the hash-method discrepancy is reviewed. The archive also contains an embedded specification rather than a separately archived copy of the canonical source file.

The supplied notebook has 22 cells but no stored execution counts or cell outputs. Therefore the archive is treated as a separate recoverable output bundle, not as proof that the notebook file itself contains an executed transcript.

## External resemblance

None asserted. The result is an internal finite predicate replay and control test.

## What this does not prove

It does not establish universal source-relation preservation, universal threshold derivation, injectivity, reversibility, theorem closure, C5/C6 status, or external physical validity.

## Failure modes and uncertainty

- Finite held-out grid and synthetic generated values.
- No flagged row is evidence only within the declared controls; it is not evidence that undiscovered counterexamples do not exist.
- Hash-method disagreement requires review before C2 result induction.
- Approved-tool replication remains outside this Colab archive.

Current disposition: `C1_ARCHIVE_PROVENANCE_PENDING_GOVERNED_INDUCTION`.
