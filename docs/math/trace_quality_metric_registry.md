# Trace Quality Metric Registry (MPF-PALG-042)

## 1. Purpose
Define metrics for source-relation trace completeness, retained-feature clarity, and loss-accounting sufficiency.

## 2. Metrics Definitions
### 2.1 Source Trace Completeness
- **Metric ID**: `source_trace_completeness`
- **Definition**: A measure of whether all required source-relation components are explicitly linked in the trace.
- **Thresholds**:
  - **GOLD**: 1.0 (All mandatory components linked)
  - **SILVER**: 0.8 (Critical components linked)
  - **BRONZE**: 0.6 (Minimum traceability)

### 2.2 Retained Feature Specificity
- **Metric ID**: `retained_feature_specificity`
- **Definition**: Evaluates whether retained features are precisely defined within the projection domain.

### 2.3 Loss Accounting Completeness
- **Metric ID**: `loss_accounting_completeness`
- **Definition**: Measures the thoroughness of documented abstractions and feature losses.

### 2.4 Projection Depth Declared
- **Metric ID**: `projection_depth_declared`
- **Definition**: Boolean check if the projection depth (PD-1 to PD-4) is explicitly stated.

### 2.5 Recoverability Class Declared
- **Metric ID**: `recoverability_class_declared`
- **Definition**: Boolean check if the recoverability class (RCOV-0 to RCOV-3) is explicitly stated.

## 3. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Trace Quality Requirements
- `source_trace_completeness >= SILVER`
- `projection_depth_declared == true`
- `loss_accounting_completeness >= 0.5`

## 5. Governance Rules
- **TQ-RULE-001**: High trace quality scores do not imply physical identity.
- **TQ-RULE-002**: Low quality scores trigger mandatory REJECT_ESCALATION.

## 6. Forbidden Claims
- Trace completeness proves source reconstruction.
- High specificity allows physical promotion.
- Metric scores replace manual audit of loss accounting.

---
[Back to Master Index](codex_master_index.md)
