# Falsification Campaign Report: FAT-25-INVARIANT-MINIMALITY

## 1. Attack Metadata and Declaration

- **Unique Attack ID:** `FAT-25-INVARIANT-MINIMALITY`
- **Target Concept:** Section 3.2A: Ordering as Structural Information
- **Target Formulation:** "Triplet identity is determined only by the minimal invariant set. Any invariant outside that set is redundant or derived. Any omitted invariant permits false equivalence."
- **Mathematical Representation:**
  - **Native Invariant Vector:**
    $$ V_{inv} = \langle I1, I2, I3 \rangle = \langle \text{Symmetry Reference}, \text{Orientation Roles}, \text{Distinction Capacity} \rangle $$
- **Explicit Assumptions:**
  - Triplet identity can be audited by removing or altering invariants one-by-one under structural perturbations.
- **Attack Boundaries:** Max steps = 1, Max models = 100.
- **Python Implementation:**
  - **Program M:** [program_m_invariant_minimality.py](file:///d:/projects/RT%20calculus/campaigns/FAT-25/program_m_invariant_minimality.py)
  - **Program S:** [program_s_invariant_minimality.py](file:///d:/projects/RT%20calculus/campaigns/FAT-25/program_s_invariant_minimality.py)
  - **Comparison:** [compare_program_results.py](file:///d:/projects/RT%20calculus/campaigns/FAT-25/compare_program_results.py)
- **Independent Verification Method:** Relational algebra proof: we mathematically prove that pointed relational structures under isomorphism define exactly three equivalence classes that correspond directly to the elements of the minimal native basis.
- **Reproducibility Information:**
  - **Python Version:** 3.12
  - **OS:** Windows
  - **Execution Command:** `python campaigns/FAT-25/compare_program_results.py`
  - **Output Artifacts:**
    - [FAT-25_PROGRAM_M_PACKET.json](file:///d:/projects/RT%20calculus/packets/FAT-25_PROGRAM_M_PACKET.json)
    - [FAT-25_PROGRAM_S_PACKET.json](file:///d:/projects/RT%20calculus/packets/FAT-25_PROGRAM_S_PACKET.json)
    - [FAT-25_COMPARISON_PACKET.json](file:///d:/projects/RT%20calculus/packets/FAT-25_COMPARISON_PACKET.json)

---

## 2. Representation Rule Declaration

- **Preserved RT Semantics:** Basis minimality and completeness.
- **Omitted RT Semantics:** None.
- **Introduced Assumptions:** We map invariants to discrete structural classes.
- **Known Projection Losses:** Standard set theory coordinate labels.
- **Falsification Conditions for the Representation:** If any structure outside the minimal set is necessary to define isomorphism, the representation is falsified.

---

## 3. Claim Boundary

- **Evidence Class:** Algebraic audit.
- **Epistemic Status:** Modeling.
- **Proof Status:** Concept supported.
- **Scope:** Foundations / Minimality.
- **Remaining Untested Assumptions:** None.
- **Applicability Level:** Concept.
- **Outcome Classification:** **TRIPLET_EQUIVALENCE_SUPPORTED**

---

## 4. Invariant Set Classification Matrix

| Invariant ID | Name | Classification | Reasoning |
| :--- | :--- | :--- | :--- |
| **I1** | Symmetry Reference | `NECESSARY` | Without >S<, orientation roles collapse and identity is lost. |
| **I2** | Orientation Roles | `NECESSARY` | Left/right roles are required to define directional distinguishability. |
| **I3** | Distinction Capacity | `NECESSARY` | Value limits of distinction slots; changing them changes identity class. |
| **I4** | Admissibility Class | `DERIVED` | Trajectories are derived from the reference relation and admissibility field. |
| **I5** | Coupling Class | `NOT_AN_INVARIANT` | Coupling governs activity and causal reach, not triplet identity. |
| **I6** | Closure Capacity | `DERIVED` | Value computed from MTO composition closure over slot capacities. |
| **I7** | Phase Signature | `HISTORICAL_ONLY` | Pre-closure history; collapsed by many-to-one MTO composition. |
| **I8** | Observed Slice | `NOT_AN_INVARIANT` | Observational projection; shifts under reorientation while identity is constant. |

---

## 5. Conclusion & Disposition

The target claim **survives** and is **supported** (outcome: **TRIPLET_EQUIVALENCE_SUPPORTED**). Both native simulation and standard pointed structure algebra agree that the minimal complete basis required to define triplet identity is $\langle I1, I2, I3 \rangle = \langle \text{Symmetry Reference}, \text{Orientation Roles}, \text{Distinction Capacity} \rangle$. All other properties are derived, historical, or activity-related.
