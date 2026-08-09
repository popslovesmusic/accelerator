# Falsification Campaign Report: FAT-18-CAUSAL-CLOSURE

## 1. Attack Metadata and Declaration

- **Unique Attack ID:** `FAT-18-CAUSAL-CLOSURE`
- **Target Concept:** Section 11.1A: Relational Basin Signatures ($\Sigma_R$)
- **Target Formulation:** "A basin is globally open and locally closed. Local closure is determined by the causal limit of distinction propagation."
- **Mathematical Representation:**
  - **Program M (Native MTO-OTM):**
    $$ \text{Propagation:} \quad x_{child} \leftarrow x_i \cdot \alpha $$
    $$ \text{Causal Basin } B := \{ i \in V \mid x_i \ge \tau \} $$
  - **Program S (Standard Mathematics):**
    $$ f(S) = S \cup \{ v \in V \mid \exists u \in S, x_u \cdot \alpha(u, v) \ge \tau_v \} $$
    $$ \operatorname{cl}(S) = \operatorname{lfp}(f) \quad (\text{Least Fixed Point under Knaster-Tarski}) $$
- **Explicit Assumptions:**
  - Attenuation ($\alpha < 1$) or non-zero thresholds ($\tau > 0$) are applied to guarantee finite reachability.
  - The graph has a directed structural substrate.
- **Attack Boundaries:** Max steps = 1, Max models = 100.
- **Python Implementation:** [attack_18_causal_closure.py](file:///d:/projects/RT%20calculus/campaigns/attack_18_causal_closure.py)
- **Independent Verification Method:** Knaster-Tarski least fixed point formulation for monotone operators on the power set poset.
- **Reproducibility Information:**
  - **Python Version:** 3.12
  - **OS:** Windows (Powershell)
  - **Execution Command:** `python campaigns/attack_18_causal_closure.py`
  - **Output Artifact:** [attack_18_dual_packet.json](file:///d:/projects/RT%20calculus/campaigns/attack_18_dual_packet.json)

---

## 2. Representation Rule Declaration

- **Preserved RT Semantics:** Basins are represented as relational admissibility windows rather than geometric path-containers.
- **Omitted RT Semantics:** Braided knot invariants ($B_K$).
- **Introduced Assumptions:** We assume that distinction propagation is modeled as discrete-step attenuation and thresholding on a graph.
- **Known Projection Losses:** We project continuous continuous-time propagation onto a discrete step reachability operator.
- **Falsification Conditions for the Representation:** If the monotone fixed-point operator fails to satisfy the algebraic closure operator axioms (reflexivity, monotonicity, idempotence), the representation fails.

---

## 3. Claim Boundary

- **Evidence Class:** Poset fixed-point theory & graph-theoretic simulation.
- **Epistemic Status:** Modeling.
- **Proof Status:** Concept survived.
- **Scope:** Topology / Basins.
- **Remaining Untested Assumptions:** Continuous time extensions.
- **Applicability Level:** Concept.
- **Outcome Classification:** **SURVIVED_SPECIFIED_ATTACK**
- **Conclusion Level:** Applies to the **Concept** level (the concept that local closure emerges from causal propagation limits without requiring geometric boundaries is mathematically consistent and validated).

---

## 4. Results & Findings

### Program M — MTO–OTM Native Decomposition
- **Propagation Expansion (M1):** Increasing attenuation factor $\alpha$ successfully expanded the basin size.
- **Propagation Reduction (M2):** Decreasing $\alpha$ successfully reduced basin size while maintaining activation order.
- **Boundary Removal (M3):** Verified that the propagation limit alone defines a closed set of updated nodes.
- **Nested Basins (M4):** Multiple roots/thresholds successfully produced nested basins.
- **Identity Stability (M5):** Activation order phase signature remained fully stable.
- **Status:** **Survives** (Alternative Hypothesis H1 holds).

### Program S — Standard Mathematical Decomposition
- **Closure Formalization (S1):** The reachability operator satisfies all algebraic closure operator axioms (reflexivity, monotonicity, idempotence).
- **Graph Reachability & Topology (S2 & S3):** Causal closure is equivalent to the reachability subset in a directed graph, which defines an Alexandroff topology on the node space.
- **Status:** **Survives**.

---

## 5. Conclusion & Disposition

The concept of **Causal Closure** has successfully **survived** this attack campaign (outcome: **SURVIVED_SPECIFIED_ATTACK**). Both the native procedural program (Program M) and standard mathematical analysis (Program S) show that local closure can emerge purely from distinction propagation limits (attenuation and thresholding) without requiring geometric coordinate boundaries. This validates the relational basin signature as a mathematically rigorous alternative to spatial containers.
