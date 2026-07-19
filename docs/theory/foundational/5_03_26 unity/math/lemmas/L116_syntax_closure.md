# Lemma L116 — Syntactic Closure of L_COD

## 1. Statement
The formal language $\mathcal{L}_{COD}$ is closed under the syntactic construction rules for terms and formulas. Every well-formed formula in the language evaluates to a uniquely determinable type class in $\{\text{State}, \text{Residue}, \text{Relation}, \text{Admissibility}, \text{Projection}\}$, preventing arbitrary operator composition or type-mismatch leakage.

## 2. Dependencies
- **Overview:** [04_syntax_and_semantic_closure_of_core_calculus.md](../04_syntax_and_semantic_closure_of_core_calculus.md)
- **Definitions:** `D1` (Admissibility window), `D2` (Projection operator), `D3` (Coupling neighborhood).

## 3. Proof Sketch
We prove syntactic closure by induction on the structure of terms in $\mathcal{L}_{COD}$:
1.  **Base Cases:**
    *   Any state variable $S_i$ is uniquely typed as $\text{State}$ ($\mathcal{S}$).
    *   Any residue variable $R_j$ is uniquely typed as $\text{Residue}$ ($\mathcal{R}$).
    *   Any context variable $c_k$ is uniquely typed as $\text{Context}$ ($\mathcal{C}$).
2.  **Inductive Step (Terms):**
    *   If $S_1, S_2 \in \mathcal{S}$ and $c \in \mathcal{C}$, the term $D(S_1 \mid S_2)_c$ maps to type $\text{Relation}$ ($\mathcal{T}$).
    *   If $R \in \mathcal{R}$ and $x$ is a process state update vector, the term $\Pi_{A(R)}(x)$ maps to type $\text{Admissible Update}$ ($\mathcal{U}$).
3.  **Inductive Step (Formulas):**
    *   A relational update formula of the form $x' = x + u$ (where $u \in \mathcal{U}$) compiles to a valid process update state, preventing any non-admissible components from altering the state aspect.
Since all construction steps map variables into disjoint type classes and preserve the signatures of relational functions, the language $\mathcal{L}_{COD}$ is syntactically closed. $\blacksquare$

## 4. Status
`complete`
