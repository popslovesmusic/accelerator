# Operator Relationship Overview

This document maps the relationships and compositions between core operators in the Mono-Process Framework.

## Core Operators

### Pi_A (Admissibility Projection)
- **Role**: Filters candidate states into the admissible window A.
- **Relationships**:
  - Composes with `delta` in continuation events.
  - Interacts with `NavT` during transport across window boundaries.

### NavT (Residue Transport)
- **Role**: Transports process residue R and orientation across the CSI domain.
- **Relationships**:
  - Bound by identity constraints in MT-002.
  - Subject to non-invertibility constraints in non-local transport scenarios.

### delta (Selection Operator)
- **Role**: Selects the next process state from a candidate set based on mismatch minimization.
- **Relationships**:
  - Must produce a non-empty image when composed with `Pi_A` (MT-003).
  - Multi-valued in degenerate minima scenarios.

## Operator Composition Table (Narrative)
- `Pi_A ∘ Pi_A`: Expected to be `Pi_A` (Idempotence, MT-001).
- `NavT(0)`: Expected to be `Identity` (MT-002).
- `Pi_A ∘ delta`: Must be non-empty for existence (MT-003).

## Governance Note
Operator relationships are mapped for conceptual clarity. Compositional closure is validated formally in `registry/math/operator_composition_registry.json`.
