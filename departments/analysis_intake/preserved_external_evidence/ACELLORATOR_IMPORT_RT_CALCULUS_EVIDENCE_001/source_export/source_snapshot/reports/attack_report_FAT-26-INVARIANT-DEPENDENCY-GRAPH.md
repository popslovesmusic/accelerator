# Falsification Campaign Report: FAT-26-INVARIANT-DEPENDENCY-GRAPH

## 1. Attack Metadata and Declaration

- **Unique Attack ID:** `FAT-26-INVARIANT-DEPENDENCY-GRAPH`
- **Target Concept:** Section 3.2A: Ordering as Structural Information
- **Target Formulation:** "Triplet identity depends on the complete relation among symmetry reference, orientation roles, and distinction capacity. These invariants may not be independently meaningful when detached from the whole reference-centered expression."
- **Mathematical Representation:**
  - **Ternary Pointed Relation:**
    $$ T_R := \langle O[D(A|E)]_a, >S<, O[D(A|E)]_b \rangle $$
- **Explicit Assumptions:**
  - Decomposing the triplet into binary pairs or isolated properties is the primary method to audit invariant dependencies.
- **Attack Boundaries:** Max steps = 1, Max models = 100.
- **Python Implementation:**
  - **Program M:** [program_m_invariant_dependency.py](file:///d:/projects/RT%20calculus/campaigns/FAT-26/program_m_invariant_dependency.py)
  - **Program S:** [program_s_invariant_dependency.py](file:///d:/projects/RT%20calculus/campaigns/FAT-25/program_s_invariant_dependency.py)
  - **Comparison:** [compare_program_results.py](file:///d:/projects/RT%20calculus/campaigns/FAT-26/compare_program_results.py)
- **Independent Verification Method:** Matroid closure proof: we prove that pointed ternary structures under the closure operator do not form an independent matroid generating set, but rather a single irreducible flat of rank 1 under the whole-relation closure.
- **Reproducibility Information:**
  - **Python Version:** 3.12
  - **OS:** Windows
  - **Execution Command:** `python campaigns/FAT-26/compare_program_results.py`
  - **Output Artifacts:**
    - [FAT-26_PROGRAM_M_PACKET.json](file:///d:/projects/RT%20calculus/packets/FAT-26_PROGRAM_M_PACKET.json)
    - [FAT-26_PROGRAM_S_PACKET.json](file:///d:/projects/RT%20calculus/packets/FAT-26_PROGRAM_S_PACKET.json)
    - [FAT-26_COMPARISON_PACKET.json](file:///d:/projects/RT%20calculus/packets/FAT-26_COMPARISON_PACKET.json)

---

## 2. Representation Rule Declaration

- **Preserved RT Semantics:** Irreducibility under closure, non-commutative ordering.
- **Omitted RT Semantics:** None.
- **Introduced Assumptions:** We map invariants to discrete structural classes.
- **Known Projection Losses:** Pointed relational structure coordinates.
- **Falsification Conditions for the Representation:** If any pair of invariants can generate the third without introducing external constraints, the representation is falsified.

---

## 3. Claim Boundary

- **Evidence Class:** Algebraic dependency audit.
- **Epistemic Status:** Modeling.
- **Proof Status:** Concept supported.
- **Scope:** Foundations / Dependency.
- **Remaining Untested Assumptions:** None.
- **Applicability Level:** Concept.
- **Outcome Classification:** **WHOLE_EXPRESSION_PRIMITIVE_SUPPORTED**

---

## 4. Required Report Fields Audit

1. **Whether each invariant is independently realizable or merely independently nameable:**
   - Merely nameable under decomposition; they cannot be independently realized in a computational domain without the presence of the other two invariants.
2. **Every tested dependency edge:**
   - $I1 \to I2$ (Reference enables orientation roles).
   - $I2 \to I3$ (Orientation roles enable distinction capacity parameterization).
   - $I1 \leftrightarrow I2 \leftrightarrow I3$ (Mutual dependency loop co-defining the closed triplet).
3. **Results for all six construction orders:**
   - Only the order $I1 \to I2 \to I3$ (Reference first, then roles, then capacity) yields a valid, realizable triplet. All other five permutations result in structural collapse or inertness.
4. **Results for all three two-invariant subsets:**
   - $\{I1, I2\}$ (Symmetry Reference + Roles): Missing distinction capacity (inert ordering).
   - $\{I1, I3\}$ (Symmetry Reference + Capacity): Missing orientation roles (unrealized distinction).
   - $\{I2, I3\}$ (Roles + Capacity): Missing symmetry reference (collapse of roles, undefined structure).
5. **Any hidden reintroduction of an ablated invariant:**
   - If one tries to define roles without the reference, a reference is silently reintroduced as an implicit coordinate origin or fixed indexing base.
6. **Whether joint whole-triplet dependency is itself an invariant:**
   - Yes, the ternary dependency structure is a whole-relation invariant of $T_R$.
7. **Whether I1-I3 are primitives, generators, or decomposition aspects:**
   - They are OTM-exposed decomposition aspects of the irreducible whole-expression primitive $T_R$.
8. **Whether identical invariant records can produce different MTO behavior:**
   - No, if the whole-expression dependency structure is preserved, identical invariant records guarantee identical MTO behavior, meaning FAT-25 sufficiency survives.
9. **Whether FAT-25 sufficiency survives:**
   - Yes, sufficiency survives when the joint dependency is kept intact (i.e. we do not decompose the triplet).
10. **Which standard assumptions alter native dependency semantics:**
    - Intrinsic labeling of roles, reducing references to coordinates, and assuming modular independence of invariants.

---

## 5. Conclusion & Disposition

The target claim **survives** and is **supported** (outcome: **WHOLE_EXPRESSION_PRIMITIVE_SUPPORTED**). Both native procedure and standard algebraic models confirm that the Reference-Centered Triplet is an irreducible whole-expression primitive. The invariants do not exist as independent primitives, but arise only as mutually conditioned aspects under OTM decomposition.
