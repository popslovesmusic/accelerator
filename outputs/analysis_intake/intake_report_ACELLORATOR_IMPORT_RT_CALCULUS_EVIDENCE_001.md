# Analysis Intake Import: ACELLORATOR_IMPORT_RT_CALCULUS_EVIDENCE_001

## Scope

Read-only preservation of the complete RT Calculus external evidence export
`RT_CALCULUS_ATTACK_EVIDENCE_20260804_002`. No review, synthesis, promotion, or RT
mutation was authorized by this import.

## Directly observed/defined

- Required export contents were present.
- Manifest and snapshot hashes matched.
- The corrected archive hash matched both `snapshot_receipt.json` and `export_record.json`.
- The transfer validation report was `VALIDATED_FOR_EXTERNAL_SUBMISSION`.
- The preserved copy contains 375 manifest-listed evidence files and 384 files including the package envelope.
- The evidence index declares 27 attacks.

## Inferred inside framework

The package is preserved as `PRESERVED_EXTERNAL_EVIDENCE`, with review status
`NOT_REVIEWED`, promotion status `HOLD`, claim ceiling `C1_model_relative`, and no
authority effect. Attack decomposition is deferred to the separate review workflow.

## External resemblance (Analogy only)

None created by this intake.

## What it does NOT prove

This import does not establish independent verification, mathematical correctness,
external validity, a cross-attack finding, a research proposition, or any change to RT.

## Failure modes / uncertainty

The source workspace was dirty at export time. That condition is retained as
provenance and must be considered during review. The archive was reissued before
this successful retry; its corrected hash is recorded in the receipt.

## Provenance

- Source: `D:\projects\RT calculus\exports\RT_CALCULUS_ATTACK_EVIDENCE_20260804_002`
- Preserved copy: `departments/analysis_intake/preserved_external_evidence/ACELLORATOR_IMPORT_RT_CALCULUS_EVIDENCE_001/source_export`
- Receipt: `departments/analysis_intake/receipts/ACELLORATOR_IMPORT_RT_CALCULUS_EVIDENCE_001.receipt.json`
- Machine report: `outputs/analysis_intake/intake_report_ACELLORATOR_IMPORT_RT_CALCULUS_EVIDENCE_001.json`

## Routing and authorization boundary

Routed to the governed Review workflow. This import creates no findings, candidate
actions, queue binding, claim promotion, registry mutation, or automatic reverse
channel into RT.
