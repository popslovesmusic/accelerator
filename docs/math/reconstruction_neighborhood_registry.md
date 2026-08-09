# Reconstruction Neighborhood Registry (MPF-RTOP-002)

## 1. Purpose
Define bounded neighborhoods describing which projections retain partial mutual reconstructability under controlled loss conditions.

## 2. Neighborhood Classes
### 2.1 RN_LOCAL_TRACE
- **Class ID**: `RN_LOCAL_TRACE`
- **Definition**: Projections sharing a direct source-relation trace with minimal deformation.

### 2.2 RN_PARTIAL_RECOVERABLE
- **Class ID**: `RN_PARTIAL_RECOVERABLE`
- **Definition**: Projections where some lost features can be recovered through multi-projection alignment.

### 2.3 RN_CONFLICT_BOUNDARY
- **Class ID**: `RN_CONFLICT_BOUNDARY`
- **Definition**: Neighborhoods defined by irreducible projection conflicts.

### 2.4 RN_DEFORMATION_LIMIT
- **Class ID**: `RN_DEFORMATION_LIMIT`
- **Definition**: Boundaries where projection distortion prevents any meaningful reconstruction.

### 2.5 RN_NONRECOVERABLE
- **Class ID**: `RN_NONRECOVERABLE`
- **Definition**: Projections completely detached from recoverable source metadata.

## 3. Metrics Definitions
### 3.1 Trace Overlap Density
- **Metric ID**: `trace_overlap_density`
- **Definition**: Measures the density of shared source metadata within a neighborhood.

### 3.2 Recoverability Locality Score
- **Metric ID**: `recoverability_locality_score`
- **Definition**: Quantifies how localized the reconstruction information is within the projection set.

### 3.3 Projection Boundary Integrity
- **Metric ID**: `projection_boundary_integrity`
- **Definition**: Evaluates whether neighborhood boundaries explicitly preserve projection distinctions.

### 3.4 Loss Isolation Clarity
- **Metric ID**: `loss_isolation_clarity`
- **Definition**: Measures if losses are isolated to specific neighborhood classes or diffused.

## 4. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 5. Governance Rules
- **RN-RULE-001**: Neighborhoods are analytic containers for comparison, not physical regions.
- **RN-RULE-002**: High overlap density does not prove source identity.

## 6. Forbidden Claims
- Reconstruction neighborhoods represent physical spacetime regions.
- High locality scores derive physical particles.
- Neighborhood alignment eliminates projection loss.

---
[Back to Master Index](codex_master_index.md)
