# Reconstruction Flow Registry (MPF-RDYN-002)

## 1. Purpose
Define bounded flow classes describing how reconstruction accessibility changes under projection transformations.

## 2. Flow Classes
### 2.1 RF_STABLE
- **Class ID**: `RF_STABLE`
- **Definition**: Flows where reconstruction accessibility remains constant or improves within bounded limits.
- **Dynamic Stability**: `STABLE`

### 2.2 RF_PARTIAL_DRIFT
- **Class ID**: `RF_PARTIAL_DRIFT`
- **Definition**: Flows where accessibility metadata begins to decouple from the local neighborhood.
- **Dynamic Stability**: `DRIFT_DETECTED`

### 2.3 RF_CONFLICT_LOCKED
- **Class ID**: `RF_CONFLICT_LOCKED`
- **Definition**: Flows that are arrested at neighborhood boundaries by irreducible projection tensions.
- **Dynamic Stability**: `STABILIZED_CONFLICT`

### 2.4 RF_DEFORMATION_CASCADE
- **Class ID**: `RF_DEFORMATION_CASCADE`
- **Definition**: Flows where projection distortion propagates and amplifies across the sequence.
- **Dynamic Stability**: `UNSTABLE`

### 2.5 RF_ACCESSIBILITY_DECAY
- **Class ID**: `RF_ACCESSIBILITY_DECAY`
- **Definition**: Flows resulting in the gradual loss of all meaningful reconstruction metadata.
- **Dynamic Stability**: `DECAYING`

### 2.6 RF_TERMINATED
- **Class ID**: `RF_TERMINATED`
- **Definition**: Flows where the reconstruction link is broken due to excessive deformation.
- **Dynamic Stability**: `NONE`

## 3. Metrics Definitions
### 3.1 Flow Trace Retention
- **Metric ID**: `flow_trace_retention`
- **Definition**: Measures the persistence of the source-relation link along a dynamic flow.

### 3.2 Recoverability Gradient
- **Metric ID**: `recoverability_gradient`
- **Definition**: The rate of change of accessibility quality across the flow sequence.

### 3.3 Projection Integrity Decay
- **Metric ID**: `projection_integrity_decay`
- **Definition**: Measures the loss of projection-domain distinctions during the flow.

### 3.4 Conflict Stability Density
- **Metric ID**: `conflict_stability_density`
- **Definition**: Evaluates if conflicts are preserved or erased in the stabilized state of the flow.

## 4. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 5. Governance Rules
- **RF-RULE-001**: Every reconstruction flow must declare its stability class and trace retention score.
- **RF-RULE-002**: Flows with `RF_DEFORMATION_CASCADE` status trigger mandatory drift detection review.

## 6. Forbidden Claims
- Stable flows prove physical conservation of information.
- Flow gradients derive physical time evolution operators.
- Accessibility decay justifies the assumption of external detachment.

## 7. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
