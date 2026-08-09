# Conflict Preservation Metric (MPF-PALG-044)

## 1. Purpose
Evaluate whether bridge artifacts preserve projection conflicts instead of erasing them into unity language.

## 2. Metrics Definitions
### 2.1 Conflict Record Completeness
- **Metric ID**: `conflict_record_completeness`
- **Definition**: Measures the fraction of identified projection-domain conflicts that are explicitly preserved in the bridge artifact.

### 2.2 Discrete/Smooth Conflict Preserved
- **Metric ID**: `discrete_smooth_conflict_preserved`
- **Definition**: Specifically tracks if the tension between discrete-transition (QM-like) and smooth-flow (GR-like) projections is maintained.

### 2.3 Threshold/Flow Conflict Preserved
- **Metric ID**: `threshold_flow_conflict_preserved`
- **Definition**: Tracks if the tension between participation-thresholding and continuous-constraint-flow is maintained.

### 2.4 Conflict Erasure Risk
- **Metric ID**: `conflict_erasure_risk`
- **Definition**: Detects language that attempts to 'resolve' or 'unify' conflicts without proper source-relation derivation.

### 2.5 Conflict Resolution Claim Blocked
- **Metric ID**: `conflict_resolution_claim_blocked`
- **Definition**: Enforcement check: all claims of conflict resolution must be blocked.

## 3. Governance Status
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true (left/right readings are incomplete without <->_R)
- **No Unification Guardrail**: No QM/GR unification, derivation, replacement, or physics claim; only analog projection behavior.
- **Theorem Status**: NOT_PROVEN
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Preservation Requirements
- `conflict_record_completeness == 1.0`
- `discrete_smooth_conflict_preserved == true`
- `threshold_flow_conflict_preserved == true`
- `conflict_resolution_claim_blocked == true`

## 5. Governance Rules
- **CPM-RULE-001**: Erasure of projection conflicts is a critical validation failure.
- **CPM-RULE-002**: Bridge artifacts must report conflicts as 'preserved' rather than 'resolved'.

## 6. Forbidden Claims
- Bridge metrics resolve the discrete/continuous conflict.
- Threshold/flow agreement eliminates projection tension.
- Conflict preservation is optional for high-coherence results.

---
[Back to Master Index](codex_master_index.md)
