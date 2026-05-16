# Projection Accessibility Relation Registry (MPF-RTOP-003)

## 1. Purpose
Formalize directional accessibility relations between projections without implying equivalence, identity, or reversibility.

## 2. Accessibility Relations
### 2.1 ACCESS_PARTIAL
- **Relation ID**: `ACCESS_PARTIAL`
- **Definition**: A directional link where some lost features of projection B can be analytically estimated from projection A.

### 2.2 ACCESS_TRACE_ONLY
- **Relation ID**: `ACCESS_TRACE_ONLY`
- **Definition**: Only the shared source-relation pointer is accessible.

### 2.3 ACCESS_CONFLICT_PRESERVING
- **Relation ID**: `ACCESS_CONFLICT_PRESERVING`
- **Definition**: Accessibility that explicitly carries the conflict metadata of the source neighborhood.

### 2.4 ACCESS_DEFORMATION_BOUND
- **Relation ID**: `ACCESS_DEFORMATION_BOUND`
- **Definition**: Accessibility limited by the maximum allowable deformation of the projected form.

### 2.5 ACCESS_BLOCKED
- **Relation ID**: `ACCESS_BLOCKED`
- **Definition**: No directional accessibility is permitted.

## 3. Mandatory Constraints
- **ACC-CON-001**: Accessibility does not imply identity.
- **ACC-CON-002**: Accessibility does not imply reversibility.
- **ACC-CON-003**: Accessibility does not imply source equivalence.

## 4. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 5. Governance Rules
- **ACC-RULE-001**: Every accessibility relation must specify directionality and reversibility status.
- **ACC-RULE-002**: Accessibility between QM-like and GR-like analogs must remain `ACCESS_CONFLICT_PRESERVING` or lower.

## 6. Forbidden Claims
- Accessibility proves that projection A is projection B.
- Mutual accessibility implies full source recovery.
- Accessibility paths derive physical interaction constants.

---
[Back to Master Index](codex_master_index.md)
