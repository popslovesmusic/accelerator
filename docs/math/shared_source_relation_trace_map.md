# Shared Source Relation Trace Map (MPF-PALG-036)

## 1. Purpose
Map QM-like and GR-like projection analogs back to indivisible ⇔R source relations while preserving projection-loss, recoverability, and conflict records.

## 2. Core Rule
- **Name**: `shared_trace_not_identity_rule`
- **Definition**: QM-like and GR-like projections may share a source relation without becoming identical, unified, or physically equivalent.
- **Short Form**: `shared_trace(QM_like, GR_like) ≠ identity(QM, GR)`

## 3. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Trace Status**: CANDIDATE_SHARED_SOURCE_TRACE_MAP
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Trace Map Schema
A valid trace map must include:
- `trace_map_id`
- `shared_source_relation`
- `qm_like_projection_ref`
- `gr_like_projection_ref`
- `qm_retained_features`
- `gr_retained_features`
- `shared_retained_features`
- `qm_lost_features`
- `gr_lost_features`
- `loss_differential`
- `conflict_records`
- `recoverability_pair`
- `claim_level`: BRIDGE_ANALOG_ONLY
- `source_identity_claim`: false
- `physical_unification_claim`: false

## 5. Governance Rules
- **SSTM-RULE-001**: Every bridge trace map must declare a shared_source_relation.
- **SSTM-RULE-002**: Shared source traceability does not imply source identity.
- **SSTM-RULE-003**: QM-like and GR-like retained features must be recorded separately before overlap is recorded.
- **SSTM-RULE-004**: Loss differentials and conflict records are mandatory.
- **SSTM-RULE-005**: Trace maps cannot be used as evidence for physical unification.

## 6. Forbidden Uses
- Using shared trace as proof of QM/GR unification.
- Collapsing QM-like and GR-like projections into one domain.
- Deleting conflict records after identifying shared source relation.
- Treating trace map as source reconstruction.
- Treating retained-feature overlap as physical evidence.

---
[Back to Master Index](codex_master_index.md)
