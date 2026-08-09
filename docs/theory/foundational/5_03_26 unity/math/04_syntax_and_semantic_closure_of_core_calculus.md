# Typed Grammar and Semantic Closure of the Core Calculus

This document formalizes the syntactic rules, semantic interpretations, and inference machinery of the Calculus of Distinction (COD) for the Mono-Process Framework. It defines the formal language $\mathcal{L}_{COD}$ to prevent ontological inflation, reification of projections, and layer slippage.

---

## 1. Syntax of $\mathcal{L}_{COD}$

### 1.1 The Alphabet
The alphabet consists of the following disjoint classes of symbols:
1.  **State Aspects ($\mathcal{S}$):** Loci of process-aspect representation, denoted by $S, S_1, S_2, \dots$
2.  **Residue Inscriptions ($\mathcal{R}$):** Constraints on future admissibility representing history, denoted by $R, R_1, R_2, \dots$
3.  **Context Operators ($\mathcal{C}$):** Parameters defining local admissibility regimes, denoted by $x, c, \alpha, \beta, \dots$
4.  **Process Updates ($\mathcal{X}$):** Dynamic updates representing process execution, denoted by $x, x', \Delta x, \dots$
5.  **Relational Operators:**
    *   Directed Distinguishability: $D(\cdot \mid \cdot)$
    *   Residue-Conditioned Biconditional: $\Leftrightarrow_R$
    *   Local Admissibility Operator: $\to_a$
    *   Projection Operator: $\Pi_A$
    *   Transition Operator: $\text{NavT}(\cdot, \cdot)$
    *   Composition Operator: $\otimes$

### 1.2 Term Rules
1.  If $S_1, S_2 \in \mathcal{S}$ and $c \in \mathcal{C}$, then the directed distinguishability relation $D(S_1 \mid S_2)_c$ is a term of type **Relational Value** ($\mathcal{V}$).
2.  If $R \in \mathcal{R}$ and $x \in \mathcal{X}$, the admissibility projection $\Pi_{A(R)}(x)$ is a term of type **Admissible Update** ($\mathcal{U}$).
3.  If $u_1, u_2 \in \mathcal{U}$, then $u_1 \otimes u_2$ is a term of type **Admissible Update** ($\mathcal{U}$).

### 1.3 Well-Formed Formulas (WFF)
A string is a Well-Formed Formula in $\mathcal{L}_{COD}$ if and only if it is constructed via the following rules:
1.  If $\mathcal{E}$ is a relational pressure and $\delta$ is an actualization operator, then $(\mathcal{E} \neq 0) \Leftrightarrow_R \delta(\mathcal{E} > 0)$ is a WFF.
2.  If $x, x' \in \mathcal{X}$ and $u \in \mathcal{U}$, then $x' = x + u$ is a WFF.
3.  If $P_{\text{adm}}(x', c, R, -(i))$ is the admissibility predicate, then $P_{\text{adm}}(x', c, R, -(i)) \in \{0, 1\}$ is a WFF.

---

## 2. Semantic Interpretation

### 2.1 Interpretation of $\Leftrightarrow_R$
The subscript $_R$ indicates that the evaluation of the biconditional is history-dependent. Formally, for a given valuation function $v$ and residue state $R_t \in \mathcal{R}$:
\[
v((\mathcal{E} \neq 0) \Leftrightarrow_R \delta(\mathcal{E} > 0)) = \text{True} \iff \text{val}(\delta(\mathcal{E} > 0) \mid R_t) = \text{val}(\mathcal{E} \neq 0)
\]
If the residue-conditioning fails to sustain non-zero distinction, the relation collapses toward the $0$-state symmetry.

### 2.2 Interpretation of the $0$-state
The $0$-state is the unique non-participating symmetry condition in which distinction $D \to 0$ and degrees of freedom $DOF \to 0$. It is defined formally as the boundary condition:
\[
0\text{-state} \notin D_{\text{domain}}
\]

---

## 3. Reference Standards
- **Standard ID:** MPF-MATH-CLOSURE-001
- **Status:** PROVISIONAL (Level C1)
- **Compliance:** [Compliance Charter v2.3](../../../../../../registry/compliance_charter_v2_3.json)
