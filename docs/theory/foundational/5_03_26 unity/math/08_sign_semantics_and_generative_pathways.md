# Sign Semantics and Generative Pathways

This document formalizes the re-conceptualization of sign polarity ($+$, $-$) as representations of active generative process pathways (Task 7.3) within the Mono-Process Framework.

---

## 1. Pathway Polarities
Rather than treating signs as arithmetic primitives, the framework defines them as directional states of relational change along process pathways:
1.  **Additive Accumulation ($+$):** Denotes the growth or addition of relational crossing layers, expanding the boundary-front neighborhood.
2.  **Exclusion Truncation ($-$):** Denotes the filtration or truncation of crossing layers, stabilizing or constricting the boundary-front.

---

## 2. Formal Sign Mapping
Let $\Delta P$ be a change along a process pathway $P$ under context $c$. We define the sign mapping function:
\[
\text{Sign}(\Delta P)_c = \left\{
  \begin{array}{ll}
  + & \text{if } \Delta_c \text{Crossings}(\Delta P) > 0 \\
  - & \text{if } \Delta_c \text{Crossings}(\Delta P) < 0 \\
  0 & \text{if } \Delta_c \text{Crossings}(\Delta P) = 0
  \end{array}
\right.
\]
where $\Delta_c \text{Crossings}(\Delta P)$ measures the net change in relational crossing crossings.

### 2.1 Process Meaning
*   **Positive step ($+$):** Increases topological complexity by introducing new interaction crossings.
*   **Negative step ($-$):** Enforces admissibility constraints by filtering out crossings that violate the local context floor $\epsilon_a$.

---

## 3. Reference Standards
- **Standard ID:** MPF-MATH-SIGN-001
- **Status:** C1_DEFINED_PROVISIONAL
- **Compliance:** [Compliance Charter v2.3](../../../../../../registry/compliance_charter_v2_3.json)
