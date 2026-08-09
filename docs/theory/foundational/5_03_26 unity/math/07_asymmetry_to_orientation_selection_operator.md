# Asymmetry-to-Orientation Selection Operator

This document establishes the mathematical bridge between relational asymmetry and orientation selection (Gap G1) within the Mono-Process Framework.

---

## 1. Bounded Asymmetry Ratio
Directed distinction between aspects is generally non-symmetric:
\[
D(S_1 \mid S_2)_c \neq D(S_2 \mid S_1)_c
\]
We define the asymmetry ratio $\Omega_a$:
\[
\Omega_a(S_1, S_2)_c = \frac{D(S_1 \mid S_2)_c}{D(S_2 \mid S_1)_c}
\]
where $D(S_1 \mid S_2)_c \ge \epsilon_a$ and $D(S_2 \mid S_1)_c \ge \epsilon_a$. The presence of the context floor $\epsilon_a > 0$ ensures the ratio remains bounded ($\Omega_a \in [\epsilon_a, \epsilon_a^{-1}]$), preventing singular division by zero.

---

## 2. Selection Operator $O^*$
The selection operator $O^*$ maps the asymmetry ratio $\Omega_a$ to the emergence of local orientation reference $-(i)$:
\[
O^*(\Omega_a)_c = -(i) \iff \Omega_a \neq 1 \wedge \text{Friction}(-(i)) = \min_{-(i') \in \mathcal{O}_{\text{adm}}} \mu_{\text{rel}}(-(i') \cdot \Omega_a)
\]
where:
*   $\mathcal{O}_{\text{adm}}$ is the set of admissible orientations.
*   $\mu_{\text{rel}}$ represents local relational pressure.

### 2.1 Symmetry Limit
If $\Omega_a = 1$ (perfect symmetry), the operator $O^*$ is undefined, meaning no intrinsic orientation selection occurs. Symmetry breaking ($\Omega_a \neq 1$) is a prerequisite for local orientation emergence.

### 2.2 Admissible Chains
Once selection occurs, the orientation sequence behaves as a directed sequence $-(i) \to -(i)+1$, representing subsequent orientation reference states rather than temporal steps.

---

## 3. Reference Standards
- **Standard ID:** MPF-MATH-ASYM-001
- **Status:** C1_DEFINED_PROVISIONAL
- **Compliance:** [Compliance Charter v2.3](../../../../../../registry/compliance_charter_v2_3.json)
