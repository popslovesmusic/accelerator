# Revised External Audit of Calculus Authority, Admission, and Projection Integrity

```json
{
  "artifact_id": "SEA-CALC-2026-07-20-002",
  "artifact_role": "GENERATED_PROJECTION",
  "authority_scope": "repository authority architecture, projection integrity, and audit interpretation",
  "canonical_source_id": "MPF_AUTHORITY_ARCHITECTURE_V1",
  "canonical_source_version": "1.0.0",
  "canonical_snapshot_id": "registry/db/acellorator_index.sqlite",
  "generated_at": "2026-07-20",
  "validator_run_id": "GV-20260720T231200.393918-1052",
  "projection_status": "current",
  "supersedes": [],
  "superseded_by": []
}
```

**Audit ID:** `SEA-CALC-2026-07-20-002`  
**Source packet:** `SEA_CALC_AUTHORITY_ARCHITECTURE_REAUDIT_2026_07_20`  
**Mode:** governed architecture clarification and reaudit after bounded repository changes  
**Claim boundary:** this audit does not promote or demote theorems, lemmas, laws, claims, lexicon terms, proof status, evidence class, or external validity.

## Architectural Authority Model

The corrected architecture is now encoded in `governance/live/authority_architecture.json`:

`HUMAN -> GOVERNED_JSON -> GOVERNED_EXTRACTION -> DATABASE -> RUNTIME -> VALIDATION -> MARKDOWN`

The key correction is directional authority. Markdown and the database are not co-equal competing operational SSOTs. Human-authored material proposes, governed JSON submits, governed extraction admits, the database carries agent operational authority, validation tests admitted state, and Markdown renders validated state for human inspection.

This reclassifies several prior audit findings. Projection drift in Markdown remains a defect, but it is not evidence that Markdown and the database are competing operational authorities.

## Admission Traceability

The repository now contains `governance/schemas/canonical_admission_packet.schema.json`, which defines the required structure for future human-originated mathematical changes entering governed admission.

Reaudit result: **CONDITIONAL_FAIL**. The schema exists, but this pass did not prove that every current runtime-authoritative Calculus object has complete human-source, submission, extraction, and admission provenance.

## Canonical Database Integrity

The new architecture identifies the canonical database as the agent operational authority. The prior DB audit in `outputs/audits/ai_db_retrieval_path_audit_2026_07_03.json` remains relevant because it classified the DB as useful but partial.

Reaudit result: **CONDITIONAL_FAIL**. The intended architecture is explicit, but complete canonical-state coverage, semantic current-state views, typed status namespaces, and dependency closure controls remain unresolved.

## Runtime Authority Enforcement

The repository now contains `runtime/policies/agent_authority_resolution.json`. It requires agents to use admitted canonical database state when available, to fail closed on deferred authority for promotions, and to avoid treating unadmitted Markdown as canonical.

Reaudit result: **CONDITIONAL_FAIL**. The policy exists, but executable negative controls have not yet demonstrated that unadmitted Markdown cannot drive governed execution.

## Validation Adequacy

The re-audit ledger enumerates required validators:

- `VAL-AUTH-PIPELINE-001`
- `VAL-RUNTIME-AUTH-001`
- `VAL-PROJECTION-TRACE-001`
- `VAL-PROJECTION-FRESHNESS-001`
- `VAL-STATUS-NAMESPACE-001`
- `VAL-CANONICAL-EXPRESSION-001`
- `VAL-WORKTREE-EVIDENCE-001`

Reaudit result: **CONDITIONAL_FAIL**. The controls are specified but not implemented as executable validators in this pass.

## Markdown Projection Integrity

The repository now contains `governance/schemas/generated_projection_metadata.schema.json`, and this report embeds projection metadata. The artifact role registry marks prior audit reports as historical records and this report as a generated projection.

Reaudit result: **CONDITIONAL_FAIL**. Primary projection metadata conventions now exist, but the main textbook and other Markdown surfaces are not yet fully stamped with canonical snapshot IDs, source object IDs, projection timestamps, and validator run identifiers.

## Prior Finding Reclassification

The machine ledger at `registry/governance/sea_calc_reaudit_finding_ledger.json` reclassifies the requested prior findings:

| Finding | Reclassification | Reaudit result |
|---|---|---|
| `SEA-CALC-F001` | Accepted with architectural qualification | Open |
| `SEA-CALC-F002` | Accepted with architectural qualification | Open |
| `SEA-CALC-F003` | Accepted | Open |
| `SEA-CALC-F004` | Accepted with architectural qualification | Partially remediated |
| `SEA-CALC-F005` | Accepted | Open |
| `SEA-CALC-F006` | Accepted with architectural qualification | Partially remediated |
| `SEA-CALC-F010` | Accepted with architectural qualification | Partially remediated |
| `SEA-CALC-F013` | Accepted | Open |

The corrected interpretation removes the specific error of treating Markdown and database state as competing operational authorities. It does not close the underlying implementation gaps.

## Residual Risks

- The DB authority layer is declared, but current coverage remains partial.
- Runtime negative controls are specified but not implemented.
- Projection metadata is not yet present across all primary Markdown documents.
- Status namespaces remain overloaded until a validator rejects untyped bare labels.
- Canonical expression variants still require object-ID based semantic resolution.
- DB freshness still needs a Git-observed dirty-worktree control.

## Final Attestation

Final result: **CONDITIONAL_FAIL**.

The revised architecture is now explicit and materially improves the interpretation of prior audit findings. The repository should no longer be audited as though Markdown and the database are competing operational SSOTs. However, the implementation does not yet satisfy the packet's acceptance criteria because provenance coverage, runtime enforcement, validator controls, and Markdown projection metadata are incomplete.

Post-write validation: `python scripts/global_validate.py` completed with run `GV-20260720T231200.393918-1052`, exit code 0, final overall status `warning`, no failed stages, and clean-pass eligibility `false`.

The appropriate next repair sequence is:

1. Implement `VAL-WORKTREE-EVIDENCE-001`.
2. Implement `VAL-PROJECTION-TRACE-001` and `VAL-PROJECTION-FRESHNESS-001`.
3. Add projection metadata to the textbook and primary reports.
4. Implement `VAL-STATUS-NAMESPACE-001`.
5. Implement `VAL-CANONICAL-EXPRESSION-001`.
6. Implement `VAL-AUTH-PIPELINE-001` and `VAL-RUNTIME-AUTH-001`.
