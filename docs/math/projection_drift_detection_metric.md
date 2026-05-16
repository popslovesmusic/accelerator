# Projection Drift Detection Metric (MPF-PALG-047)

## 1. Purpose
Detect when projection language drifts toward primitive ontology, physical interpretation, arithmetic replacement, or unification claims.

## 2. Metrics Definitions
### 2.1 Primitive Promotion Drift
- **Metric ID**: `primitive_promotion_drift`
- **Definition**: Detects use of projection outcomes as if they were irreducible framework primitives.

### 2.2 Physical Language Drift
- **Metric ID**: `physical_language_drift`
- **Definition**: Detects physical-theory terms applied to projection analogs without 'like' or 'analog' qualifiers.

### 2.3 Identity Language Drift
- **Metric ID**: `identity_language_drift`
- **Definition**: Detects language implying that a projection IS the source relation.

### 2.4 Unification Language Drift
- **Metric ID**: `unification_language_drift`
- **Definition**: Detects early escalation to unification or physical law derivation.

### 2.5 Reconstruction Overclaim Drift
- **Metric ID**: `reconstruction_overclaim_drift`
- **Definition**: Detects claims that projection coherence proves the source relation is now fully understood or recovered.

## 3. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Drift Thresholds
- **WARNING**: 0.3 (Minor linguistic drift detected)
- **BLOCK**: 0.6 (Critical governance violation; escalation rejected)

## 5. Governance Rules
- **PDD-RULE-001**: Any drift score exceeding the BLOCK threshold triggers automatic REJECT_ESCALATION.
- **PDD-RULE-002**: Drift detection is mandatory for all C4+ claim submissions involving bridges.

## 6. Forbidden Claims
- Drift detection scores are subjective.
- Linguistic drift does not impact technical validity.
- Implicit unification is permitted if metrics are high.

---
[Back to Master Index](codex_master_index.md)
