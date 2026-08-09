# Falsification Campaign Report: FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT

## 1. Attack Metadata and Declaration

- **Unique Attack ID:** `FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT`
- **Target Concept:** Section 3.1: The Admissibility Filter
- **Target Formulation:** "Admissibility is a reference-conditioned relational field of available organization. The causal window is not the admissibility field itself; it is the domain-relative limit at which distinction can no longer propagate through active coupling. Beyond that limit, the condition becomes locally closed and causally inert in the tested domain while potentially remaining coupled elsewhere."
- **Mathematical Representation:**
  - **Program M (Native MTO-OTM):**
    $$ \text{Admissibility Field } AF_R \subseteq V \times V $$
    $$ \text{Active Coupling } K_D \subseteq AF_R $$
    $$ \text{Causal Reach } CL_D := \{ y \in V \mid \text{reachable}(x, y) \text{ under } K_D \} $$
  - **Program S (Standard Mathematics):**
    $$ G_{\text{global}} = (V, AF_R) \quad \text{and} \quad G_{\text{active}} = (V, K_D) \quad \text{where} \quad K_D \subseteq AF_R $$
- **Explicit Assumptions:**
  - The admissibility field ($AF_R$) is globally open and does not change when coupling changes.
  - Causal propagation travels along active coupling relations ($K_D$).
- **Attack Boundaries:** Max steps = 1, Max models = 100.
- **Python Implementation:** [attack_22_admissibility_field_causal_limit.py](file:///d:/projects/RT%20calculus/campaigns/attack_22_admissibility_field_causal_limit.py)
- **Independent Verification Method:** Directed graph component reachability analysis: we prove that reachability partitions a graph into closed components (basins) without needing any distance metric or coordinates.
- **Reproducibility Information:**
  - **Python Version:** 3.12
  - **OS:** Windows (Powershell)
  - **Execution Command:** `python campaigns/attack_22_admissibility_field_causal_limit.py`
  - **Output Artifact:** [attack_22_dual_packet.json](file:///d:/projects/RT%20calculus/campaigns/attack_22_dual_packet.json)

---

## 2. Representation Rule Declaration

- **Preserved RT Semantics:** Admissibility field represents possible transitions, whereas causal reach represents active transitions.
- **Omitted RT Semantics:** Structural residue memory.
- **Introduced Assumptions:** We represent relations as directed pairs in sets.
- **Known Projection Losses:** We project onto simple set-theoretic graphs, losing qualitative orientation nuances.
- **Falsification Conditions for the Representation:** If standard graph theory cannot distinguish between possible paths and currently active paths, the representation is falsified.

---

## 3. Claim Boundary

- **Evidence Class:** Graph-theoretic and reachability analysis.
- **Epistemic Status:** Modeling.
- **Proof Status:** Concept survived.
- **Scope:** Topology / Causal Relations.
- **Remaining Untested Assumptions:** None.
- **Applicability Level:** Concept.
- **Outcome Classification:** **SURVIVED_SPECIFIED_ATTACK**
- **Conclusion Level:** Applies to the **Concept** level (the concept that admissibility field and causal limit are mathematically distinct structures is validated).

---

## 4. Required Report Fields Audit

1. **Whether admissibility and causal limitation were independently varied:**
   - Yes, the admissibility field ($AF_R$) was held fixed while the active coupling set ($K_D$) was varied, proving that the causal reach limit can contract/expand independently of the field.
2. **Whether coupling was modeled without adjacency:**
   - Yes, coupling was modeled purely as a set of ordered relational tuples (relations) rather than as a numeric matrix or spatial distance.
3. **Whether ordinal orientation replaced primitive time:**
   - Yes, propagation was modeled purely as ordinal path connectivity (relational dependency sequence) rather than as temporal steps.
4. **Whether domain-relative zero DoF was distinguished from global inactivity:**
   - Yes, setting $DoF_A(z) = 0$ in Domain A left $z$ inert in Domain A, but $z$ remained active in Domain B ($DoF_B(z) > 0$), proving that zero degrees of freedom is domain-relative and does not imply global inactivity or nonexistence.
5. **Whether indirect influence required a complete lawful coupling chain:**
   - Yes, indirect influence of $x$ on $z$ required a complete multi-domain path: $x \to y$ in Domain B compositionally coupled to $y \to z$ in Domain A.
6. **Whether local closure emerged or was imposed:**
   - Local closure emerged naturally at the boundary where active coupling terminated, rather than being imposed by external geometric boundaries.
7. **What remained globally available after local closure:**
   - The global admissibility field ($AF_R$) remained completely open and intact, preserving all other possible transitions.
8. **Which representation losses occurred:**
   - Directed graphs represent relations as discrete points (vertices) and arrows (edges), losing the continuous relational tension of process orientations.

---

## 5. Conclusion & Disposition

The concept of **Admissibility Field and Causal Limit Separation** has successfully **survived** this attack campaign (outcome: **SURVIVED_SPECIFIED_ATTACK**). Both the native procedure (Program M) and standard mathematics (Program S) agree that available possible transitions (Admissibility Field) and active reach (Causal Limit) are distinct structures, and local closure emerges naturally from coupling termination.
