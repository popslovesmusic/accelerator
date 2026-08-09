# Cross-Projection Loss Differential Matrix (MPF-PALG-037)

## 1. Purpose
Track what QM-like and GR-like projections each preserve, lose, and distort relative to their shared ⇔R source relation.

## 2. Core Rule
- **Name**: `differential_loss_not_contradiction_rule`
- **Definition**: QM-like and GR-like projections may preserve different aspects of a shared ⇔R source relation without either projection invalidating the other.
- **Short Form**: `loss_difference(QM_like, GR_like) ≠ contradiction`

## 3. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Matrix Status**: CANDIDATE_CROSS_PROJECTION_LOSS_DIFFERENTIAL
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Matrix Schema
A valid matrix record must include:
- `matrix_id`
- `shared_source_relation`
- `qm_like_projection_ref`
- `gr_like_projection_ref`
- `qm_preserved_features`
- `gr_preserved_features`
- `shared_preserved_features`
- `qm_lost_features`
- `gr_lost_features`
- `qm_distortion_risks`
- `gr_distortion_risks`
- `differential_status`
- `claim_level`: BRIDGE_ANALOG_ONLY
- `physical_unification_claim`: false

## 5. Governance Rules
- **CPLD-RULE-001**: Loss differentials must be recorded shorthand:before bridge coherence is evaluated.
- **CPLD-RULE-002**: Differential preservation cannot be interpreted as physical complementarity.
- **CPLD-RULE-003**: Projection distortion risks must be recorded for both domains.
- **CPLD-RULE-004**: Projection disagreement does not automatically imply source-relation contradiction.
- **CPLD-RULE-005**: Projection agreement does not imply source-relation recovery.

## 6. Forbidden Uses
- Using loss differentials as proof of QM/GR complementarity.
- Treating QM-like loss as GR-like superiority.
- Treating GR-like loss as QM-like superiority.
- Collapsing projection distortions into physical claims.
- Using differential matrix as theorem evidence.

---
[Back to Master Index](codex_master_index.md)


---
**source_relation**: (E≠0) ⇔R δ(E>0)
**non_separability_acknowledged**: non-separability acknowledged
