# Projection Depth Taxonomy (MPF-PALG-022)

## 1. Purpose
This document establishes the **Projection Depth Taxonomy**. It classifies projection operators (Πx) by their structural flattening depth and retained fidelity to the simultaneous recursive aspect-binding ($\iff_R$) core. This ensures that the "information cost" of mathematical simplification is rigorously quantified.

## 2. Depth Levels (PD-1 to PD-4)

### PD-1: shallow_projection
- **Definition**: Retains source traceability, aspect context, and limited residue metadata while reducing expression complexity.
- **Risk**: LOW.

### PD-2: moderate_projection
- **Definition**: Retains traceability but abstracts simultaneity into directional or comparative symbolic forms.
- **Risk**: MEDIUM.

### PD-3: deep_projection
- **Definition**: Produces ordinary symbolic structures (e.g., $=, \to, \circ, \iff$) with minimal source traceability.
- **Risk**: HIGH.
- **Constraint**: Requires a mandatory warning that source reconstruction is not available from the projected form alone.

### PD-4: terminal_projection
- **Definition**: Output is highly flattened; reconstruction is impossible without external trace metadata.
- **Risk**: CRITICAL.
- **Constraint**: Cannot be used as evidence for primitive relation structure.

## 3. Depth Governance Rules
- **PDT-RULE-001**: Every projection must explicitly declare its `projection_depth`.
- **PDT-RULE-002**: Deep and terminal projections are marked as high-risk and inherently lossy.
- **PDT-RULE-003**: Fidelity to the source relation is treated as a decreasing function of projection depth.

## 4. Default Assignments
The primary projection operators are classified at **PD-3 (Deep Projection)**:
- **Π_equal**: Flattens recursive binding into substitutability.
- **Π_imply**: Sequentializes simultaneous aspects.
- **Π_compose**: Orders co-presence into structural chaining.
- **Π_biconditional**: Reduces process closure to reciprocal truth.

## 5. Usage Rules
- **Banned**: Using PD-3 or PD-4 projections as proof of primitive relational dynamics.
- **Banned**: Omitting depth classification in analytical reports.
- **Banned**: Claiming that flattening preserves full holistic semantics.

## 6. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Taxonomy Status**: CANDIDATE_PROJECTION_TAXONOMY.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.

---
[Back to Master Index](codex_master_index.md)
