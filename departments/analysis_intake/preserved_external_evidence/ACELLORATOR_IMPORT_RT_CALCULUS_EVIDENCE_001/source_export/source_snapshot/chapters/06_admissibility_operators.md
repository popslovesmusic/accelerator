# Chapter 6: Admissibility Operators

## 6.1 The Filter of the Possible: $\delta_a$

As established in Chapter 1, the process does not transition into any arbitrary state. The set of potential continuations is constrained by the **Admissibility Filter**, denoted as $\delta_a$. This filter is constrained by the **Admissibility Window** ($A(c)$), which acts as the structural constraint filtering raw difference into persistence [Source: MPF-CORE-V1 Sec 1.3].

**Formal Statement 6.1.1: The Admissibility Predicate**
$$ P_{\text{adm}}(x', c, R, -(i)) = \Gamma_{\mathcal{E}} \land \Gamma_R \land \Gamma_T \land \Gamma_{\mathcal{O}} $$

**Commentary:**
The operator $\delta_a$ uses a predicate $P_{\text{adm}}$ to evaluate candidate continuations. This predicate is the mathematical representation of the "laws" of the system at step $k$. A state is admissible only if it satisfies all four constituent constraint families ($\Gamma$):
1. **Mismatch Preservation ($\Gamma_{\mathcal{E}}$):** Non-null distinction maintenance.
2. **Residue Compatibility ($\Gamma_R$):** History-conditioned legality.
3. **Topology Compatibility ($\Gamma_T$):** Admissible organization class.
4. **Orientation Compatibility ($\Gamma_{\mathcal{O}}$):** Directional alignment.

This conjunctive kernel separates the abstract logical check from mechanism-specific realization (e.g., PDE-specific topology rules) [Source: PADM_GAMMA_SEPARATION_001].

---

## 6.1A The Composition of $\delta_a$

The Admissibility Filter is not a single irreducible action, but a **composition of three functional operations** that transform a constraint condition ($\mathcal{E} \neq 0$) into a realized state ($\mathcal{E} > 0$).

**Formal Block 6.1.2: The Update Composition Rule**
$$ \delta_a(x;c) := \Pi_A \left( S(\text{Cand}(x;c);c) ; c \right) $$

**Functional Components (The Operational Funnel):**
1. **$\text{Cand}$ (Candidate Generation):** Proposes the full possibility space based on current **position** (where you are) [Source: MS-SCRATCH-V1 Sec 5.1].
2. **$S$ (Selection/Pruning):** A sequential pruning stage internal to $\delta_a$ and upstream of $\text{Arb}_A$. In the current provisional registry form, $S_{R,A}(C_t) \to C_t^S$ removes candidate continuations that fail type admissibility, nonzero distinction, residue compatibility, topology preservation, or orientation compatibility before realization arbitration. $S$ does not select the realized continuation, does not increase candidate-set cardinality, and does not depend on post-realization outcomes [Source: VAL-S-ARB-001; registry/math/s_arbitration_validation_registry.json].
3. **$\Pi_A$ (Admissibility Projection):** The enforcer of **residue** (what history permits). It maps surviving candidates onto the admissible window $A(c)$ [Source: MS-SCRATCH-V1 Sec 3.2].

**Definition 6.1.3: Admissibility Projection ($\Pi_A$ or $\Pi_{A_\alpha}$)**
An operator that filters a candidate increment (such as an aggregate transport contribution $y_\alpha$) into the local admissibility window $A_\alpha$ before a state update is applied. Formally defined as mapping the candidate input to the closest admissible configuration:
$$ \Pi_{A_\alpha}(y_\alpha) := \{ z_\alpha \in A_\alpha : d_A(z_\alpha, y_\alpha) = \inf_{u \in A_\alpha} d_A(u, y_\alpha) \} $$
where $d_A$ is the metric on the candidate space. Under stable conditions, the projection is boundedly idempotent:
$$ \Pi_{A_\alpha}(\Pi_{A_\alpha}(y_\alpha)) = \Pi_{A_\alpha}(y_\alpha) $$
and preserves boundary cases (where the admissibility margin is zero) as structural features rather than failures [Source: MPF_LEX_ADMISSIBILITY_PROJECTION_RESOLUTION_001].

**Commentary:**
This composition rule is the mechanism of realization. It defines how the abstract necessity of the Primary Axiom is procedurally manifested. The funnel narrows from raw potentiality ($\text{Cand}$) through intentional bias ($S$) to historical legality ($\Pi_A$), resulting in the admissible set from which a single event will be realized [Source: MPF-IND-ARB-DELTA-DUAL-PHASE IND-002].

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
This notation indicates that state $A$ permits a transition to state $B$ *given orientation* $-(i_a)$. If the orientation were to shift to $-(i_b)$, the admissibility of $B$ might change. In the current induction layer, this is better read as relational progression: admissible organization is rewritten across the orientation space $\mathcal{O}$, and any field-dynamics wording remains a downstream projection rather than the primitive ontology. [Source: RT-IND-2026-07-19-RELATIONAL-PROGRESSION-001]

---

## 6.4 Admissibility Failure: The Empty Set Condition

A critical aspect of the framework is the possibility of **Admissibility Failure**, occurring when the composition $\delta_a$ returns the empty set ($\emptyset$).

**Formal Block 6.4.1: The Two-Level Fork (IND-003)**
When $\delta_a(x;c) = \emptyset$, the process faces a structured fork resolved by $\text{Arb}_A$ at a higher level:

1. **Branch 1: Re-orientation (Crisis Regime):**
   If the residue $R$ can reopen the admissibility window under a different orientation $-(i)$, $\text{Arb}_A$ selects a new orientation reference rather than a new state. The landscape shifts, and what was blocked becomes open. "If you cannot move from where you are standing, you change where you are standing from" [Source: MPF-IND-ARB-DELTA-DUAL-PHASE].

2. **Branch 2: Collapse (0-state Regime):**
   If available orientations are exhausted and the window remains empty, the right side of the Primary Axiom fails. The closure decouples, and the framework collapses into the **0-state**.
   $$ \neg [ (\mathcal{E} \neq 0) \iff_R \delta_a(\mathcal{E} > 0) ] \to 0\text{-state} $$

**Commentary:**
The 0-state is not just process termination; it is the collapse of the conditions under which existence was possible. Process existence is not a static given; it is continuously earned by the availability of admissible continuation.

**Deferred Expansion Note:**
This section is a provenance-explicit partial section: it was found structurally incomplete during repository audit and was deferred while the RT Calculus v1.0 campaign established the governed continuation, evaluation, failure-classification, recursion, fixed-point, and projection surfaces. The deferral records repository state and campaign scope; it does not mean the incompleteness was an original design objective.

**Governed RT Calculus Support**
- Continuation failure is represented by diagnostic failure objects rather than lawful continuation objects. See `PATCH_PI_RT_CALCULUS_022` and `PATCH_PI_RT_CALCULUS_023`.
- Failure classification and evaluation order are governed by the RT Calculus v1.0 surfaces. See `PATCH_PI_RT_CALCULUS_024` and `PATCH_PI_RT_CALCULUS_025`.
- Recursive continuation and fixed-point interaction are available as bounded comparison/evaluation machinery. See `PATCH_PI_RT_CALCULUS_037` through `PATCH_PI_RT_CALCULUS_045`.
- These surfaces clarify the operational handling of $\delta_a = \emptyset$ but do not by themselves introduce recovery semantics.

**Provenance Cross-Reference (PATCH_PI_RT_CALCULUS_051):**
The empty-admissibility fork above is the local failure boundary for this chapter. Applied patches 046-049 supply the governed support for explicit RT rebinding, A/E asymmetry, projection provenance, and invariant handling; recovery and return-to-stable-regime semantics remain deferred.

**Formal Failure-Boundary Reduction (APPENDIX_F_CH6_4_PROVENANCE_ADMISSIBILITY_FAILURE_REDUCTION_001):**
The provenance-explicit Chapter 6.4 obligation is reduced at the diagnostic-failure level. When the admissibility image is empty, the governed continuation-calculus reading is:
$$ \delta_a(x;c)=\emptyset \Rightarrow \bot_C^{\mathrm{adm}} $$
where $\bot_C^{\mathrm{adm}}$ is a diagnostic failure classification rather than a lawful continuation object. The two-level fork is therefore read as a classified boundary condition:
$$ \bot_C^{\mathrm{adm}} \Rightarrow \{\mathrm{Reorient}(R,O,c),\ 0\text{-state collapse}\}_{\mathrm{diagnostic}} $$
This records the available diagnostic alternatives without asserting that either branch has already been formalized as a recovery operator. In particular:
$$ \mathrm{Recover}(\bot_C^{\mathrm{adm}})\ \text{is undefined here} $$
$$ \mathrm{ReturnStable}(\bot_C^{\mathrm{adm}})\ \text{is undefined here} $$
This reduction closes the Appendix F obligation to define the provenance-explicit failure boundary, while leaving recovery and return-to-stable-regime semantics as separate future formalization work. It does not modify $RT_{core}$, does not prove 0-state collapse, and does not promote any failure branch to theorem status.

**Coverage Matrix**
| Topic | Status | Action |
| --- | --- | --- |
| empty admissibility trigger | retained_in_6_4 | keep |
| two-level fork between reorientation and collapse | retained_in_6_4 | keep |
| failure classification | covered_by_rt_calculus_v1_0 | cross_reference |
| evaluation order | covered_by_rt_calculus_v1_0 | cross_reference |
| recursive continuation | covered_by_rt_calculus_v1_0 | cross_reference |
| fixed-point interaction | covered_by_rt_calculus_v1_0 | cross_reference |
| provenance-explicit failure boundary | scoped_resolved_diagnostic | cite_APP_F_reduction_001 |
| recovery branch | not_covered | defer_explicitly |
| return-to-stable-regime | not_covered | defer_explicitly |
| 0-state collapse proof | not_proven_here | preserve_as_claim_level_limited |

---

## 6.5 Governed Status of the Admissibility Kernel

The theorem-status registry currently labels the following three objects `FORMALLY_PROVEN` at `C6_formal_closure`. The synchronized audit does not treat those labels alone as sufficient proof authority because the cited proof note contains premises that are not discharged in the registered source surface. Until that conflict is reviewed, these objects remain registry claims under qualification and cannot transfer C6 status to downstream projections.

1.  **The Admissibility Predicate $P_{\text{adm}}$:** Formally defined as a conjunctive boolean kernel: $P_{adm} = \Gamma_{\mathcal{E}} \land \Gamma_R \land \Gamma_T \land \Gamma_{\mathcal{O}}$ [Source: PADM_GAMMA_SEPARATION_001].
2.  **Composition and Image Existence (`THM_PADM_001`):** The registered argument depends on an available minimum, which requires a finite admissible set or separately stated compactness/attainment conditions, plus a declared tie-break rule. Those premises are not yet discharged by the registered proof surface.
3.  **Crisis Fork Trigger (`THM_PADM_002`):** The registered argument is exhaustive only if reorientation is the sole remaining admissible degree of freedom after failure. That premise is not yet discharged by the registered proof surface; recovery semantics remain deferred.
4.  **Non-Transitivity (`THM_PADM_003`):** The registered counterexample requires distinct residue states and an orientation-sensitive admissibility change. Those witness conditions are not yet discharged by the registered proof surface.

**Current evidence class:** `C1_REGISTRY_STATUS_CONFLICT_REVIEW_REQUIRED`. This qualification does not silently rewrite the theorem-status registry; it blocks unqualified textbook inheritance while proof-source admission, assumptions, and status-namespace semantics are reconciled.

---

---

## Summary of Chapter 6 Dependencies

- **Chapter 1** introduced $\delta_a$ in the core expression.
- **Chapter 2** showed how $R$ conditions $\delta_a$.
- **Chapter 9** will explore the **Directional Coupling** ($\to_a \otimes \gets_r$) between admissibility and residue support.
- **Chapter 10** will show how **Arb_A** (Arbitration) selects a single realized state from the set provided by $\delta_a$.

By formalizing the admissibility operators, we move from the static "existence" of the process to the "selection" mechanics that govern its specific path and character.

\pagebreak

