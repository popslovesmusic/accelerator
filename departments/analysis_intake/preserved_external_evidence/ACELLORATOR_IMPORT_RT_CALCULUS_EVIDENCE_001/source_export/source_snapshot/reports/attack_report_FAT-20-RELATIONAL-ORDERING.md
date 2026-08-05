# Falsification Campaign Report: FAT-20-RELATIONAL-ORDERING

## 1. Attack Metadata and Declaration

- **Unique Attack ID:** `FAT-20-RELATIONAL-ORDERING`
- **Target Concept:** Section 3.2A: Ordering as Structural Information
- **Target Formulation:** "Relational ordering is primitive. Coupling is an admissible consequence of relational ordering rather than adjacency, metric distance, topology, or temporal succession."
- **Mathematical Representation:**
  - **Program M (Native MTO-OTM):**
    $$ \text{Relations Set } R := \{ (X, Y), (Y, Z), (Z, X) \} $$
    $$ \text{Coupling}(A, B) \iff (A, B) \in R $$
  - **Program S (Standard Mathematics):**
    $$ \text{Poset Antisymmetry:} \quad X \le Y \land Y \le Z \land Z \le X \implies X = Y = Z \quad (\text{Set Collapse}) $$
    $$ \text{Category Identity:} \quad \operatorname{id}_A \implies \text{Zero distinction loop} \implies \text{Collapse by Axiom 1.2.1} $$
- **Explicit Assumptions:**
  - Relational ordering can contain reciprocal feedback cycles (loops).
  - Poset models require the antisymmetry axiom.
- **Attack Boundaries:** Max steps = 1, Max models = 100.
- **Python Implementation:** [attack_20_relational_ordering.py](file:///d:/projects/RT%20calculus/campaigns/attack_20_relational_ordering.py)
- **Independent Verification Method:** Relational algebra proof: we show that any binary relation on a set $X$ containing a cycle collapses $X$ to a singleton set under the quotient map induced by the antisymmetric closure equivalence relation.
- **Reproducibility Information:**
  - **Python Version:** 3.12
  - **OS:** Windows (Powershell)
  - **Execution Command:** `python campaigns/attack_20_relational_ordering.py`
  - **Output Artifact:** [attack_20_dual_packet.json](file:///d:/projects/RT%20calculus/campaigns/attack_20_dual_packet.json)

---

## 2. Representation Rule Declaration

- **Preserved RT Semantics:** Relational ordering is structural information that precedes metric asymmetry.
- **Omitted RT Semantics:** Distinction density ($\rho_D$).
- **Introduced Assumptions:** We represent native ordering as a set of directed pairs.
- **Known Projection Losses:** We project native ordering onto standard posets and categories, which enforce constraints (antisymmetry, identity morphisms) that collapse dynamic cycles.
- **Falsification Conditions for the Representation:** If a standard poset or category can represent a non-trivial cyclic relation without collapse or extra structure, the representation is falsified.

---

## 3. Claim Boundary

- **Evidence Class:** Algebraic & set-theoretic model checks.
- **Epistemic Status:** Modeling.
- **Proof Status:** Disagreement located.
- **Scope:** Foundations.
- **Remaining Untested Assumptions:** None.
- **Applicability Level:** Representation.
- **Outcome Classification:** **PROJECTION_FALSIFIED**
- **Conclusion Level:** Applies to the **Representation** level (standard posets/preorders cannot represent cyclic feedback ordering without collapse, proving a representation loss in standard mathematics, while the native relational ordering successfully operates as a primitive).

---

## 4. Results & Findings

### Program M — MTO–OTM Native Decomposition
- **Adjacency & Metric Ablation (M1-M3):** Successfully traced path $X \to Y \to Z \to X$ purely from the set of relations, without adjacency matrices, metrics, or temporal succession.
- **Topological Ablation (M4):** Basins defined as downward-closed subsets remained valid.
- **Coupling & Propagation (M5 & M6):** Coupling and propagation successfully emerged from the relations.
- **Status:** **Survives** (Alternative Hypothesis H1 holds).

### Program S — Standard Mathematical Decomposition
- **Poset Antisymmetry (S1):** Poset representation of the cycle collapsed the set size from 3 to 1, destroying coordinates.
- **Category identity (S2):** Identity morphisms represent zero distinction loops, which collapse the state under Axiom 1.2.1.
- **Status:** **Fails** (standard representations collapse cyclic ordering).

---

## 5. Conclusion & Disposition

The target claim **survives** as a native concept, but its standard mathematical projection is **falsified** (outcome: **PROJECTION_FALSIFIED**). The disagreement locates a fundamental boundary: standard order theory cannot represent reciprocal feedback relations without collapse due to the antisymmetry axiom, whereas the native RT calculus successfully treats Relational Ordering as an irreducible primitive that supports cyclical dynamics without losing structural information.
