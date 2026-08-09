# Notebook 22 Result Review

## Scope

Review of the executed Notebook 22 archive testing an enriched typed relation-token witness against the bounded `PreserveRelation_C` candidate predicate.

## Directly observed/defined

The archive contains four rows: two bare-witness rows and two enriched-witness rows. Bare relation-identity checks fail in both cases; enriched relation-token checks pass in both cases. The endpoint projection collides across the two source cases.

## Inferred inside framework

Within the declared two-case model, carrying an explicitly linked relation token is sufficient for the candidate predicate used by the notebook, while the bare projection is insufficient for relation identity.

## External resemblance (Analogy only)

None asserted.

## What it does NOT prove

It does not establish universal source-relation preservation, injectivity, information preservation, theorem closure, or physical validity.

## Failure modes / uncertainty

The model has two deterministic cases, the internal manifest lacks per-file output hashes, and source-semantic status of relation tokens remains unestablished. Approved-tool replication and promotion above C2 remain blocked.

## Disposition

`C2_LIMITATION_OR_NEGATIVE_RESULT`. OBL-D-001D and OBL-D-001E remain `OPEN`; the C1 formal claim ceiling is unchanged, while this notebook artifact is classified at the Colab evidence ceiling C2 for its bounded limitation result.
