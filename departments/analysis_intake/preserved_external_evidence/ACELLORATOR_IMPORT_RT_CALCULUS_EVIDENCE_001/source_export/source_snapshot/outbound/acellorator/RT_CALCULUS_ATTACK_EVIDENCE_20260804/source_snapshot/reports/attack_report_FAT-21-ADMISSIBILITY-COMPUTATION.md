# Falsification Campaign Report: FAT-21-ADMISSIBILITY-COMPUTATION

## 1. Attack Metadata and Declaration

- **Unique Attack ID:** `FAT-21-ADMISSIBILITY-COMPUTATION`
- **Target Concept:** Section 3.1: The Admissibility Filter
- **Target Formulation:** "A finite orientation domain possesses computational capability only relative to a reference operating through an admissibility sphere."
- **Mathematical Representation:**
  - **Program M (Native MTO-OTM):**
    $$ \text{Candidates:} \quad C_k := \{ \theta_k - 1, \theta_k, \theta_k + 1 \} $$
    $$ \text{Admissibility Filter:} \quad \text{Adm}(C_k) := \{ \theta \in C_k \mid |\theta - \text{ref}| \le w \} $$
  - **Program S (Standard Mathematics):**
    $$ \text{Turing Machine transition:} \quad \delta(q, \sigma) = (q', \sigma', d) \quad (\text{No observer reference gating}) $$
- **Explicit Assumptions:**
  - Computation is defined as the convergence or stabilization of the state trajectory.
  - Standard models of computation assume absolute, un-gated transition functions.
- **Attack Boundaries:** Max steps = 1, Max models = 100.
- **Python Implementation:** [attack_21_admissibility_computation.py](file:///d:/projects/RT%20calculus/campaigns/attack_21_admissibility_computation.py)
- **Independent Verification Method:** Rewrite system analysis: we show that removing rule guards in a rewrite system results in non-determinism and divergence, destroying structured computation.
- **Reproducibility Information:**
  - **Python Version:** 3.12
  - **OS:** Windows (Powershell)
  - **Execution Command:** `python campaigns/attack_21_admissibility_computation.py`
  - **Output Artifact:** [attack_21_dual_packet.json](file:///d:/projects/RT%20calculus/campaigns/attack_21_dual_packet.json)

---

## 2. Representation Rule Declaration

- **Preserved RT Semantics:** Admissibility gating is necessary to transform orientation into computation.
- **Omitted RT Semantics:** Rotational character ($\chi$).
- **Introduced Assumptions:** We represent orientations as scalar angles and admissibility as a phase window.
- **Known Projection Losses:** We project qualitative admissibility gating onto a simple numerical window, representing observer relativity as angle difference.
- **Falsification Conditions for the Representation:** If conventional computation models can represent observer-relative gating as a primitive without loss of semantics, the representation fails.

---

## 3. Claim Boundary

- **Evidence Class:** State-trajectory and computational theory analysis.
- **Epistemic Status:** Modeling.
- **Proof Status:** Disagreement located.
- **Scope:** Foundations / Computation.
- **Remaining Untested Assumptions:** None.
- **Applicability Level:** Representation.
- **Outcome Classification:** **PROJECTION_FALSIFIED**
- **Conclusion Level:** Applies to the **Representation** level (standard computation models suffer from representation loss by omitting observer-relative gating as a primitive, while the native admissibility filter successfully acts as a primitive operator driving computation).

---

## 4. Results & Findings

### Program M — MTO–OTM Native Decomposition
- **Ablation & Saturation (M1 & M3):** Removing or saturating admissibility led to unstabilized random walks, collapsing structured computation.
- **Reference Variation (M2):** Shifting the reference successfully shifted the attractor states.
- **Single Admissible Face (M4):** Narrowing the window to $0.1$ successfully generated strictly deterministic convergence.
- **Dynamic Admissibility (M5):** Shifting reference dynamically successfully changed observed trajectories.
- **Observer Independence (M6):** Two references computed different admissible trajectories from the same substrate.
- **Status:** **Survives** (Alternative Hypothesis H1 holds).

### Program S — Standard Mathematical Decomposition
- **Constraint Satisfaction (S1 & S2):** Validly models admissibility as guards on rewrite rules.
- **Countermodel (S3 & S4):** Conventional Turing machines and lambda calculus compute without observer-relative gating, assuming absolute laws, representing a representation loss of the observer's role in computing.
- **Status:** **Fails**.

---

## 5. Conclusion & Disposition

The target claim **survives** as a native concept, but its standard mathematical projection is **falsified** (outcome: **PROJECTION_FALSIFIED**). The disagreement locates a fundamental boundary: conventional computer science models transitions as absolute and observer-independent, whereas the native RT calculus successfully treats Admissibility relative to an observer reference as the primitive operator necessary to drive and stabilize computation.
