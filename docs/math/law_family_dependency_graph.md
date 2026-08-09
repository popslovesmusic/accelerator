# Law Family Dependency Graph (MPF-LAW-CONS-006)

## 1. Purpose
Define the dependency relationships between law families to clarify the framework's logical hierarchy and ensure that all derivations trace correctly back to foundational axioms without introducing hidden globality or circular assumptions.

## 2. Dependency Graph
| Family ID | Name | Depends On | Role in Stack |
| :--- | :--- | :--- | :--- |
| **LF-001** | admissibility_and_selection | None | Foundational selection and boundary logic. |
| **LF-002** | orientation_accessibility | LF-001 | Accessibility depends on valid selection and reach. |
| **LF-003** | projection_time_geometry | LF-001 | Projection requires defined admissibility sets. |
| **LF-004** | basin_channel_identity | LF-001, LF-002, LF-003 | Basin persistence requires stable selection, transport, and projection. |
| **LF-005** | reconstruction_loss | LF-003 | Loss accounting requires active projection tracking. |
| **LF-006** | failure_transition | LF-001, LF-004 | Failures propagate from selection gaps and basin collapse. |
| **LF-007** | multiscale_and_grammar | All | Arbitration and grammar govern the composition of the entire stack. |

## 3. Governance Status
- **Theorem Status**: NO_THEOREM_PROMOTION
- **Series Status**: LAW_CONSOLIDATION_ONLY
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 4. Governance Rules
- **LDG-RULE-001**: Every family must have at least one documented dependency or be marked as foundational (LF-001).
- **LDG-RULE-002**: Dependency links must not imply global closure or physical causality.

## 5. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
