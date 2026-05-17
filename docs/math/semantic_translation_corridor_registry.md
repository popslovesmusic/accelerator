# Semantic Translation Corridor Registry (MPF-RSEM-005)

## 1. Purpose
Define bounded semantic translation pathways between reconstruction domains without implying equivalence or reversibility.

## 2. Corridor Classes
### 2.1 STC_PARTIAL_ALIGNMENT
- **Class ID**: `STC_PARTIAL_ALIGNMENT`
- **Definition**: Translation pathways where specific invariants are preserved.
- **Stability**: `STABLE_INVARIANTS`

### 2.2 STC_TRACE_COMPATIBLE
- **Class ID**: `STC_TRACE_COMPATIBLE`
- **Definition**: Translation dependent on shared source-relation trace metadata.
- **Stability**: `TRACE_DEPENDENT`

### 2.3 STC_CONFLICT_LOCKED
- **Class ID**: `STC_CONFLICT_LOCKED`
- **Definition**: Pathways restricted by mandatory conflict preservation.
- **Stability**: `CONSTRAINED`

### 2.4 STC_DEFORMATION_HEAVY
- **Class ID**: `STC_DEFORMATION_HEAVY`
- **Definition**: Translation paths involving significant interpretive distortion.
- **Stability**: `UNSTABLE`

### 2.5 STC_TRANSLATION_BLOCKED
- **Class ID**: `STC_TRANSLATION_BLOCKED`
- **Definition**: Cross-domain semantic mapping is prohibited.
- **Stability**: `NONE`

## 3. Corridor Properties
### 3.1 Semantic Trace Overlap
- **Property ID**: `semantic_trace_overlap`
- **Definition**: Measures alignment of interpretive metadata.

### 3.2 Conflict Preservation Requirement
- **Property ID**: `conflict_preservation_requirement`
- **Definition**: Boolean check if corridor preserves domain tensions.

### 3.3 Translation Loss Visibility
- **Property ID**: `translation_loss_visibility`
- **Definition**: Quantifies explicit accounting for meaning loss.

### 3.4 Recoverability Stability
- **Property ID**: `recoverability_stability`
- **Definition**: Evaluates persistence under further transformation.

## 4. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 5. Governance Rules
- **STC-RULE-001**: Every translation corridor must specify its alignment class and loss visibility score.
- **STC-RULE-002**: Semantic translation does not imply reversibility, equivalence, or source-identity recovery.

## 6. Forbidden Claims
- Perfect semantic translation proves physical substrate identity.
- Translation corridors derive universal physical constants.
- Alignment stability justifies the assumption of a 'common language'.

## 7. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
