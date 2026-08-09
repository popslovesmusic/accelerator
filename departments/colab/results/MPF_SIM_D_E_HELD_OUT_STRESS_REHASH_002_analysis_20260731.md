# Notebook 23 REHASH-002 result analysis

## Scope

This is a corrected deterministic re-run of the frozen `MPF_SIM_D_E_HELD_OUT_STRESS_001` design using the REHASH-002 source notebook. It is not a new experiment and does not reuse the prior excluded archive as an input.

## Directly observed

- Archive SHA-256: `a3e6b47abe6242bbf2019b8de26ac940b2337f132aaca7f6e970f49dfd62472e`.
- Internal artifact hashes: all match the manifest.
- Frozen specification hash: matches under the corrected frozen serialization method.
- 324 rows completed.
- 324/324 control agreements.
- 324/324 replay agreements.
- 0 falsification flags.
- The new row payload is byte-identical to the prior excluded archive’s row payload.

## Inferred inside the framework

The run reproduces the same bounded finite classifications under the same frozen contexts, cases, seeds, and replay policy. This is deterministic repeatability evidence for the declared design, not independent sampling evidence.

## External resemblance

None asserted.

## What it does not prove

It does not establish universal source-relation preservation, threshold derivation, injectivity, reversibility, theorem closure, C5/C6 status, or external physical validity.

## Failure modes and uncertainty

- The output rows match the prior excluded archive byte-for-byte; this limits novelty and independence.
- The embedded specification retains the original source-notebook path for the frozen spec; the external processing manifest binds the replacement notebook hash.
- The finite grid and deterministic seeds remain bounded.
- Approved-tool replication remains pending.

Disposition: `C2_LIMITATION_OR_NEGATIVE_RESULT` candidate, pending governed induction review; not for textbook or claim-registry insertion.
