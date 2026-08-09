# Minimal Theorem Dependency Binding (MPF-FSUB-009)

## 1. Purpose
Bind MT-001, MT-002, and MT-003 explicitly to the formal substrate objects they require to prepare for proof-candidate work.

## 2. Theorem Bindings
### 2.1 MT-001: Projection Idempotence
- **Required Substrate**: `Pi_A signature`, `A_alpha definition`, `projection_equivalence`, `Im_A definition`.
- **Preconditions**: idempotence preconditions.
- **Failure Modes**: `projection_non_idempotence`.

### 2.2 MT-002: Transport Identity
- **Required Substrate**: `NavT signature`, `orientation space (omega_alpha)`, `transport_equivalence`, `CSI_alpha neighborhood`.
- **Preconditions**: identity transport preconditions.
- **Failure Modes**: `transport_identity_failure`.

### 2.3 MT-003: Non-Empty Admissible Image
- **Required Substrate**: `delta selection semantics`, `admissible image definition (Im_A)`, `residue space (R_alpha)`, `selection rules`.
- **Preconditions**: mismatch non-null ($\mathcal{E} \neq 0$).
- **Failure Modes**: `admissible_image_empty`, `selection_undefined`.

## 3. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Series Status**: FORMAL_SUBSTRATE_SCAFFOLD
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Governance Rules
- **TDB-RULE-001**: No MT target may be promoted to proof candidate without complete substrate binding.
- **TDB-RULE-002**: Substrate objects must be formally defined and validated before theorem dependency is confirmed.

## 5. Forbidden Claims
- Theorem binding proves that the theorem is true.
- Dependency coverage makes the substrate ontologically complete.
- Binding eliminates the risk of hidden undefined primitives.

## 6. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
