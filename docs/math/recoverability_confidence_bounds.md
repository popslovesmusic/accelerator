# Recoverability Confidence Bounds (MPF-PALG-046)

## 1. Purpose
Define confidence bounds for trace-recoverability while blocking claims of full source reconstruction.

## 2. Confidence Bounds Definitions
### 2.1 RCOV_CONF_0: None
- **Bound ID**: `RCOV_CONF_0`
- **Definition**: No confidence in recoverability; trace is broken or missing.
- **Allowable Claims**: None.

### 2.2 RCOV_CONF_1: Trace Pointer Only
- **Bound ID**: `RCOV_CONF_1`
- **Definition**: Confidence in basic source-relation linkage, but no context is recoverable.
- **Allowable Claims**: `analog_linkage`.

### 2.3 RCOV_CONF_2: Partial Context
- **Bound ID**: `RCOV_CONF_2`
- **Definition**: Confidence in recovering some aspect roles and loss categories.
- **Allowable Claims**: `constrained_analog_analysis`.

### 2.4 RCOV_CONF_3: Reentry-Ready Reference
- **Bound ID**: `RCOV_CONF_3`
- **Definition**: High confidence in trace-metadata completeness for re-entering whole-relation analysis.
- **Allowable Claims**: `governed_relation_reentry`.

## 3. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Governance Rules
- **RCB-RULE-001**: Projected forms cannot reconstruct ⇔R by themselves, regardless of confidence bound.
- **RCB-RULE-002**: Confidence bounds apply to trace metadata quality, not source-relation truth.

## 5. Forbidden Claims
- Projected forms reconstruct ⇔R by themselves.
- RCOV_CONF_3 allows physical identity claims.
- Trace confidence replaces loss accounting requirements.

---
[Back to Master Index](codex_master_index.md)
