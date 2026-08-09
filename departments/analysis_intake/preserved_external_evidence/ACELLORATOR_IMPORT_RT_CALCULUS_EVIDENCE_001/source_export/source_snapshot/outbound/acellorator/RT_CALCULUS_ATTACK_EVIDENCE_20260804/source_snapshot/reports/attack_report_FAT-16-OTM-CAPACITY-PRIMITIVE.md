# Falsification Campaign Report: FAT-16-OTM-CAPACITY-PRIMITIVE

## 1. Attack Metadata and Declaration

- **Unique Attack ID:** `FAT-16-OTM-CAPACITY-PRIMITIVE`
- **Target Concept:** Section 3.1E: Relational Capacity and the $n$ Subscript
- **Target Formulation:** "OTM assumes Capacity. Distinction is not a prerequisite of OTM. MTO assumes Distinction as part of realization."
- **Mathematical Representation:**
  - **Program M (Native MTO-OTM):**
    $$ \operatorname{OTM}((D)_n) \to \{ \text{axis}_1, \dots, \text{axis}_n \} \quad \text{where} \quad D(\text{axis}_i | \text{axis}_j) = \text{unrealized} $$
  - **Program S (Standard Mathematics):**
    $$ I = \{1, 2, \dots, n\} \implies \text{requires} \quad \forall i, j \in I, i \neq j \quad (\text{pre-existing distinguishability}) $$
- **Explicit Assumptions:**
  - OTM can execute using blank, unvalued coordinate slots (axes) to represent relational capacity $n$.
  - MTO realization requires assigning specific values to these slots, introducing differences (distinctions).
- **Attack Boundaries:** Max steps = 1, Max models = 100.
- **Python Implementation:** [attack_16_otm_capacity_primitive.py](file:///d:/projects/RT%20calculus/campaigns/attack_16_otm_capacity_primitive.py)
- **Independent Verification Method:** Relational algebra proof: we show that standard set cardinality requires a distinguishability relation to prevent collapse to a singleton set.
- **Reproducibility Information:**
  - **Python Version:** 3.12
  - **OS:** Windows (Powershell)
  - **Execution Command:** `python campaigns/attack_16_otm_capacity_primitive.py`
  - **Output Artifact:** [attack_16_dual_packet.json](file:///d:/projects/RT%20calculus/campaigns/attack_16_dual_packet.json)

---

## 2. Representation Rule Declaration

- **Preserved RT Semantics:** Distinction is required for MTO realization but not for OTM allocation.
- **Omitted RT Semantics:** Relational alignment ($\langle * \rangle_x$).
- **Introduced Assumptions:** We assume that set-theoretic cardinality is the standard mathematical representation of capacity $n$.
- **Known Projection Losses:** Set theory cannot represent "empty coordinate slots" without defining distinct elements, creating an unavoidable dependency on distinguishability.
- **Falsification Conditions for the Representation:** If standard set theory can represent a set with cardinality $n > 1$ without any identity or distinguishability relation, the representation is falsified.

---

## 3. Claim Boundary

- **Evidence Class:** Algebraic & set-theoretic model checks.
- **Epistemic Status:** Provisional / modeling.
- **Proof Status:** Disagreement located.
- **Scope:** Foundations / OTM-MTO calculus.
- **Remaining Untested Assumptions:** None.
- **Applicability Level:** Representation vs. Formulation.
- **Outcome Classification:** **PROJECTION_FALSIFIED**
- **Conclusion Level:** Applies to the **Representation** level (standard set theory cannot project capacity without presupposing distinguishability, while the native procedural calculus successfully instantiates capacity as primitive coordinate slots).

---

## 4. Results & Findings

### Program M — MTO–OTM Native Decomposition
- **OTM Allocation (M1 & M2):** Successfully allocated $n=3$ blank coordinate channels without requiring any active distinction values.
- **Capacity Ablation (M3):** Setting $n=0$ successfully collapsed the OTM channels, proving dependency on $n$.
- **MTO Boundary (M5):** During MTO realization, assigning identical values to all channels collapsed all differences to $0.0$, causing MTO realization to fail.
- **Status:** **Survives** (Alternative Hypothesis H1 holds procedurally).

### Program S — Standard Mathematical Decomposition
- **Set-Theoretic Representation (S1 & S2):** Bypassing distinguishability collapsed the index set cardinality representing capacity $n=3$ to $1$, making it impossible to represent any capacity $n > 1$.
- **Status:** **Fails** (standard mathematics requires distinguishability to represent coordinates).

---

## 5. Conclusion & Disposition

The target claim **survives** as a native procedural concept, but its standard mathematical projection is **falsified** (outcome: **PROJECTION_FALSIFIED**). The disagreement locates a fundamental boundary: standard set theory has a representation loss where it cannot formalize dimensions or coordinates without defining distinct elements, whereas the native RT calculus successfully treats Relational Capacity as a primitive slots generator independent of realized distinctions.
