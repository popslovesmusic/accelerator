# Projection Recoverability Limits (MPF-PALG-023)

## 1. Purpose
This document defines the conditions under which projected forms can (or cannot) be used to reconstruct their originating **⇔R** (residue-bound equivalence) source relations. It establishes that projections are inherently "non-recoverable" by default, requiring external trace metadata for re-entry into governed whole-relation analysis.

## 2. Core Rule: Non-Recoverability
A projection output cannot reconstruct its original ⇔R source relation unless external trace metadata preserves the lost aspect, residue, and source-relation context.
- **Short Form**: $\boxed{ \Pi_x(A \iff_R B) \nrightarrow \text{recover}(A \iff_R B) }$

## 3. Recoverability Classes

### RCOV-0: not_recoverable
Projected form lacks sufficient source metadata for reconstruction. This is the state of most ordinary symbolic expressions.

### RCOV-1: trace_recoverable
Projected form can point back to its source relation through external trace metadata (e.g., a `trace_id`), but the symbolic expression itself cannot internally reconstruct the relation.

### RCOV-2: partially_context_recoverable
Projected form preserves enough internal metadata to recover specific aspect roles, but full simultaneity or residue-history remains lost.

### RCOV-3: restricted_whole_reference_recoverable
Projected form preserves the source pointer, aspect roles, and loss accounting sufficient to formally re-enter governed whole-relation analysis.

## 4. Recoverability Defaults
Primary projections are classified as **RCOV-1 (Trace Recoverable)**:
- **Equality ($=$)**: Retains substitutability; requires external trace for residue-history.
- **Implication ($\to$)**: Preserves direction; requires external trace for mutuality.
- **Composition ($\circ$)**: Preserves ordering; requires external trace for co-presence.
- **Biconditional ($\iff$)**: Preserves reciprocal truth; requires external trace for process closure.

## 5. Minimum Metadata for Re-entry
Re-entering a whole-relation state from a projection requires:
- `source_relation` identifier.
- `projection_operator_id`.
- `projection_depth` (PD-1 to PD-4).
- `aspect_roles`.
- `retained_features` and `lost_or_abstracted_features`.
- Explicit `non_separability_acknowledged` boolean.

## 6. Forbidden Claims
- Claiming a projection output reconstructs ⇔R by itself.
- Claiming a deep projection (PD-3) can serve as evidence for primitive relation structure.
- Erasing the recoverability limits to bypass governance reviews.

## 7. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Governance Status**: CANDIDATE_RECOVERABILITY_LIMITS.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.

---
[Back to Master Index](codex_master_index.md)
