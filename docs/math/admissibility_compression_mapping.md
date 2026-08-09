# Admissibility Compression Mapping (MPF-PAR-005)

## 1. Purpose
Determine whether the multiple admissibility-related structures and rules developed during the substrate formalization and review phases can be compressed into a smaller number of governed families. This mapping simplifies the admissibility logic while preserving full coverage of selection, projection, transport, and orientation constraints.

## 2. Admissibility Families
| Family ID | Member Types and Sub-Rules | Status |
| :--- | :--- | :--- |
| **AF-001: Selection and Boundary** | `selection_admissibility`, `window_constraints`. | `COMPRESSED` |
| **AF-002: Projection and Observability** | `projection_admissibility`, `aspect_visibility`. | `COMPRESSED` |
| **AF-003: Transport and Accessibility** | `transport_admissibility`, `path_admissibility`. | `COMPRESSED` |
| **AF-004: Orientation and Alignment** | `orientation_admissibility`, `frame_alignment`. | `COMPRESSED` |

## 3. Findings
All existing admissibility logic is successfully mapped to these four stabilized families. No "orphan" admissibility rules were detected.

## 4. Governance Status
- **Theorem Status**: PARTICIPATORY_REFINEMENT_ONLY
- **Series Status**: POST_PFS_REFINEMENT_PHASE
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 5. Governance Rules
- **ACM-RULE-001**: Every admissibility structure must map to one of the four stabilized families.

## 6. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true (left/right interpretations are locally valid but incomplete without <->_R)

---
[Back to Master Index](codex_master_index.md)
