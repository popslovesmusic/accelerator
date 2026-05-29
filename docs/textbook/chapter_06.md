# Chapter 6: Admissibility Operators

## 6.1 The Filter of the Possible: $\delta_a$

As established in Chapter 1, the process does not transition into any arbitrary state. The set of potential continuations is constrained by the **Admissibility Filter**, denoted as $\delta_a$. This filter is constrained by the Admissibility Window ($A$), which acts as the structural constraint filtering raw difference into persistence [Source: MPF-CORE-V1 Sec 1.3].

**Formal Statement 6.1.1: The Admissibility Predicate**
$$ \delta_a(\mathcal{E}_k) \to \{ \mathcal{E}_{k+1} \mid P_{\text{adm}}(\mathcal{E}_{k+1}, \mathcal{E}_k, R, -(i)) = \text{true} \} $$
$$ P_{\text{adm}} := [ \text{MISSING DEFINITION: Formal admissibility predicate} ] $$

**Commentary:**
The operator $\delta_a$ uses a predicate $P_{\text{adm}}$ to evaluate candidate continuations. This predicate is the mathematical representation of the "laws" of the system at step $k$. A state is admissible only if it satisfies the constraints imposed by the current mismatch ($\mathcal{E}$), the historical residue ($R$), and the selected orientation ($-(i)$).

---

## 6.2 Directional Admissibility: $\to_a$ and $\gets_a$

Admissibility is inherently directional. We distinguish between the forward-facing selection of a next state and the reverse-facing validation of that state.

**Formal Block 6.2.1: Directional Operators**
$$ A \to_a B : \text{Forward admissibility (A permits B)} $$
$$ A \gets_a B : \text{Reverse admissibility (B is supported by A)} $$

**Commentary:**
$\to_a$ is the **proactive** component of the filter: it maps from the current state to the set of allowed future states. $\gets_a$ is the **reactive** or **validating** component: it checks if a proposed future state is compatible with the "ground" provided by the current state. In many regimes, these are symmetric, but near boundaries or transitions, $A \to_a B$ may be true while $B \gets_a A$ fails (directional occlusion).

---

## 6.3 Orientation-Conditioned Admissibility

As established in Chapter 5, direction requires an orientation. The $\to_a$ operator is typically indexed or conditioned by the current orientation reference $-(i)$. This follows the universal update law $X' = \{x_\alpha + \Pi_{A_\alpha}(-(i)_\alpha[\varepsilon_\alpha, r_\alpha])\}$ [Source: MPF-CORE-V1 Sec 4.3].

**Formal Block 6.3.1: Oriented Continuation**
$$ A \to_a(-(i_a)) B $$

**Commentary:**
This notation indicates that state $A$ permits a transition to state $B$ *given orientation* $-(i_a)$. If the orientation were to shift to $-(i_b)$, the admissibility of $B$ might change. This is the foundation for the derivation of field dynamics: the "motion" or "flow" of the process is governed by how $\to_a$ shifts across the orientation space $\mathcal{O}$.

---

## 6.4 Admissibility Failure

A critical aspect of the framework is the possibility of **Admissibility Failure**.

**Formal Block 6.4.1: Failure Condition**
$$ \delta_a(\mathcal{E}_k) = \emptyset \implies \text{Process Termination or Re-orientation Necessity} $$

**Commentary:**
If no candidate continuation satisfies $P_{\text{adm}}$, the process faces a singular condition. This may result in the "death" of the local process (zero-collapse) or, more commonly, it forces a radical **re-orientation** ($k \to \text{Arb}_A$) to find a new orientation where the window of admissibility is once again open.

---

## 6.5 Missing and Provisional Formalisms

To achieve formal closure for the admissibility program, the following must be induced:

1.  **The Admissibility Predicate $P_{\text{adm}}$:** [ **MISSING DEFINITION** ] What is the exact algebraic check? Does it involve a threshold on $\mathcal{E}$, a conservation of $R$-invariants, or a topological braid-matching rule?
2.  **Composition Rules for $\to_a$:** [ **MISSING DEFINITION** ] If $A \to_a B$ and $B \to_a C$, does $A \to_a C$ follow? The associativity and transitivity of admissibility are not assumed.
3.  **Admissibility Boundaries:** [ **REQUIRES INDUCTION** ] How do we formally define the "edge" of the admissibility window $\mathcal{A}$? Is it a sharp cutoff or a dissipative gradient?

---

## Summary of Chapter 6 Dependencies

- **Chapter 1** introduced $\delta_a$ in the core expression.
- **Chapter 2** showed how $R$ conditions $\delta_a$.
- **Chapter 9** will explore the **Directional Coupling** ($\to_a \otimes \gets_r$) between admissibility and residue support.
- **Chapter 10** will show how **Arb_A** (Arbitration) selects a single realized state from the set provided by $\delta_a$.

By formalizing the admissibility operators, we move from the static "existence" of the process to the "selection" mechanics that govern its specific path and character.
