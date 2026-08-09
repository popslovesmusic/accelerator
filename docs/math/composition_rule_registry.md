# Composition Rule Registry (MPF-FSUB-006)

## 1. Purpose
Define valid and invalid operator compositions while blocking hidden sequentialization of simultaneous aspect-binding.

## 2. Composition Classes
### 2.1 VALID_LOCAL_COMPOSITION
- **Class ID**: `VALID_LOCAL_COMPOSITION`
- **Definition**: Operator composition within the same local neighborhood where domains and codomains align exactly.

### 2.2 VALID_PROJECTED_COMPOSITION
- **Class ID**: `VALID_PROJECTED_COMPOSITION`
- **Definition**: Composition of projected operators where loss declaration is explicit.

### 2.3 REQUIRES_LOSS_DECLARATION
- **Class ID**: `REQUIRES_LOSS_DECLARATION`
- **Definition**: Composition that implies a reduction in aspect dimensionality or simultaneity.

### 2.4 INVALID_DOMAIN_MISMATCH
- **Class ID**: `INVALID_DOMAIN_MISMATCH`
- **Definition**: Composition where codomain/domain do not align.

### 2.5 INVALID_SEQUENTIALIZATION
- **Class ID**: `INVALID_SEQUENTIALIZATION`
- **Definition**: Attempting to compose simultaneous aspect roles into a chronological sequence.

### 2.6 INVALID_IDENTITY_COLLAPSE
- **Class ID**: `INVALID_IDENTITY_COLLAPSE`
- **Definition**: Composition that assumes output $\equiv$ input without mapping.

## 3. Mandatory Rules
- **CR-RULE-001**: Composition is projection-derived unless explicitly restricted.
- **CR-RULE-002**: Composition cannot replace the core relation ⇔R.
- **CR-RULE-003**: Every composition must declare domain/codomain compatibility and associated loss.
- **CR-RULE-004**: Projected composition must declare lost simultaneity or retained structure.

## 4. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Series Status**: FORMAL_SUBSTRATE_SCAFFOLD
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 5. Forbidden Claims
- Operator composition proves physical causality.
- Associative composition derives physical law invariance.
- Composition without loss recovers the whole source relation.

## 6. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
