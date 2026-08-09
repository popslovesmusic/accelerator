# Formal Theorem Statements (MPF-RFPR-002)

## 1. Purpose
Normalize the structure of theorem statements for MT-001, MT-002, and MT-003 under explicit locality and assumption constraints to prepare for formal external-style scrutiny.

## 2. Normalized Statements
### 2.1 MT-001: Restricted Projection Idempotence
- **Formal Statement**: $\Pi_A \circ \Pi_A \sim \Pi_A$ within stable local neighborhood $Neighborhood_\alpha$.
- **Declared Assumptions**:
  - $A1$: The local admissibility set $A_\alpha$ is non-empty and bounded.
  - $A2$: The residue-conditioning $\mathcal{R}$ remains stable during iteration.
  - $A3$: The neighborhood is free of `recursive_divergence`.
- **Domain Scope**: `STRICTLY_LOCAL`.
- **Equivalence**: `projection_equivalence`.
- **Failure Condition**: `projection_non_idempotence`.

### 2.2 MT-002: Restricted Transport Identity
- **Formal Statement**: $NavT(x_\alpha, \omega_\alpha, \alpha \to \beta) \equiv (x_\alpha, \omega_\alpha)$ under `transport_equivalence`.
- **Declared Assumptions**:
  - $A1$: Neighborhood accessibility is maintained across the index traversal.
  - $A2$: Path flux remains within local stability thresholds (finite flux).
  - $A3$: Orientation minimization remains well-posed.
- **Domain Scope**: `STRICTLY_LOCAL`.
- **Equivalence**: `transport_equivalence`.
- **Failure Condition**: `transport_identity_failure`.

### 2.3 MT-003: Non-Empty Admissible Image
- **Formal Statement**: $\delta(Im_A) \neq \emptyset$ under non-null mismatch condition $(\mathcal{E} \neq 0)$.
- **Declared Assumptions**:
  - $A1$: Selection pressure is active (non-null mismatch).
  - $A2$: A subset of $A_\alpha$ remains reachable within the local $CSI$ reach.
  - $A3$: Selection rules are formally defined and non-contradictory.
- **Domain Scope**: `STRICTLY_LOCAL`.
- **Equivalence**: `none` (existence proof).
- **Failure Condition**: `admissible_image_empty`.

## 3. Mandatory Governance Statement
**Left-only and right-only interpretations are locally valid but incomplete without $\iff_R$ inseparability.**

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
