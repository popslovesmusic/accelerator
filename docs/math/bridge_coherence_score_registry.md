# Bridge Coherence Score Registry (MPF-PALG-045)

## 1. Purpose
Define analog-only coherence scores for comparing projection alignment without implying identity, source recovery, or unification.

## 2. Metrics Definitions
### 2.1 Shared Trace Score
- **Metric ID**: `shared_trace_score`
- **Definition**: Measures the alignment of source-relation pointers between compared projections.

### 2.2 Feature Overlap Score
- **Metric ID**: `feature_overlap_score`
- **Definition**: Quantifies the structural similarity between retained features in distinct domains.

### 2.3 Loss Compatibility Score
- **Metric ID**: `loss_compatibility_score`
- **Definition**: Evaluates whether the losses in one domain are consistent with the preserved features in the other.

### 2.4 Recoverability Alignment Score
- **Metric ID**: `recoverability_alignment_score`
- **Definition**: Measures if compared projections share a consistent recoverability class or target context.

### 2.5 Coherence Without Identity Score
- **Metric ID**: `coherence_without_identity_score`
- **Definition**: A composite score reflecting alignment while penalizing claims that drift toward identity or unification.

## 3. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Coherence Requirements
- `shared_trace_score >= 0.9`
- `feature_overlap_score >= 0.4`
- `coherence_without_identity_score <= 0.8`

## 5. Governance Rules
- **BCS-RULE-001**: Coherence scores are indicators of analog alignment, not source truth.
- **BCS-RULE-002**: Score results cannot be used as theorem evidence for unification.

## 6. Forbidden Claims
- High coherence scores prove source identity.
- Feature overlap derives shared physical laws.
- Compatibility scores eliminate the need for conflict preservation.

---
[Back to Master Index](codex_master_index.md)
