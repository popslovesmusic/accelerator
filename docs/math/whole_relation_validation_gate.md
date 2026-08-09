# Whole-Relation Validation Gate (MPF-PALG-008)

## 1. Purpose
This document defines the **Whole-Relation Validation Gate**. This gate ensures that any process-algebra artifact analyzing specific aspects, projections, or domain analogies remains strictly traceable to an indivisible source relation. It rejects artifacts that treat analytical convenience as ontological separation or unearned primitive status.

## 2. Core Rule: No Aspect Without Source
Any artifact that analyzes a part of a recursive process relation must explicitly preserve its trace to the indivisible whole relation and must not promote that part to independent primitive status.
- **Short Rule**: $\boxed{ \text{No aspect without source relation.} }$

## 3. Mandatory Gate Checks
The gate enforces the following criteria:
- **WRG-001 (source_relation_required)**: Every aspect or projection must declare its `source_relation`.
- **WRG-002 (non_separability_acknowledged)**: Every isolated aspect must acknowledge non-separability from the whole.
- **WRG-003 (primitive_status_false)**: Traced aspects must not be promoted to `primitive_status=true`.
- **WRG-004 (loss_accounting_required)**: Projections must record what was `lost_or_abstracted`.
- **WRG-005 (claim_level_restricted)**: Claims must not exceed `ANALOG_MODEL_ONLY`.
- **WRG-006 (no_physics_escalation)**: No claims of physical proof or QM/GR unification.
- **WRG-007 (no_arithmetic_replacement)**: No claims of replacing standard arithmetic.
- **WRG-008 (operator_fragmentation_guard)**: New operators must not fragment the primary relation.

## 4. Failure Conditions
An artifact fails the gate if it:
- Misses the source relation link.
- Sets `primitive_status=true` without formal promotion governance.
- Projects without accounting for feature loss.
- Uses escalated language (e.g., "proof of reality", "universal unification").
- Treats an aspect as a standalone, fundamental entity.

## 5. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Gate Status**: CANDIDATE_VALIDATION_GATE.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.

---
[Back to Master Index](codex_master_index.md)
