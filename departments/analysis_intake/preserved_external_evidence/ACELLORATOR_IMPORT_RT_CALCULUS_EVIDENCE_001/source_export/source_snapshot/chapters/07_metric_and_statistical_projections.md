# Chapter 7: Metric and Statistical Projections

## 7.1 From Relation to Measurement

As established in Chapter 3, the fundamental measure of mismatch in the Mono-Process Framework is the relational value $D(S_1|S_2)$. However, for this framework to interface with empirical data or external physical theories, these internal relational values must be mapped to measurable scalar quantities. This mapping is known as **Metric Projection**.

**Formal Statement 7.1.1: The Metric Extraction**
$$ \text{Meas} : \mathcal{X} \times \mathcal{C} \to \mathbb{R}^d $$

**Commentary:**
The extractor $\text{Meas}$ (alternatively $\iff_m$) converts the abstract process states $\mathcal{X}$ under context $\mathcal{C}$ into a shared measurement space (typically $\mathbb{R}^d$). This map allows for the comparison of different mechanism classes and the generation of comparable traces $y_t$ [Source: MS-SCRATCH-V1 Sec 8.1].

In the applied 048-049 witness sequence, this conversion is read as a projection-layer readout rather than a primitive identity claim: it preserves comparability while remaining distinct from the source relation and from $RT_{core}$.

---

## 7.2 The Asymmetry Ratio: $\Omega_a$

A primary derived metric for characterizing the orientation bias of a process is the **Asymmetry Ratio ($\Omega_a$)**, defined as $\Omega_a = x/z$ where $x$ and $z$ are the directed distinctions [Source: TECH-NOTE-ASYM Sec 2].

**Formal Block 7.2.1: Asymmetry Ratio Definition**
$$ \Omega_a := \frac{D(S_1|S_2)}{D(S_2|S_1)} $$

**Commentary:**
$\Omega_a$ (Omega_a) measures the **projected asymmetry** of the domain. It is critical to note that **$\Omega_a$ is not asymmetry itself**, nor does it define the asymmetry domain. Rather, it quantifies the relational imbalance after metric extraction from a pre-existing structural asymmetry [Source: MPF-REFINE-V2 RI-004]. 
- If $\Omega_a = 1$, the domain is symmetric ($symm\_app$).
- If $\Omega_a \neq 1$, the domain is asymmetric ($asym\_app$).

Within the governed 047-049 witness family, this remains a metric readout of asymmetry rather than a symmetry law. The ratio records projected imbalance, but it does not itself define symmetry or erase role asymmetry.
By utilizing the **floor $\epsilon$** (see Chapter 8), we ensure $\Omega_a$ remains finite and well-defined. Statistical projection ($ \iff_s $) may estimate $\Omega_a$ through observed probabilities, but the underlying relational asymmetry remains structural.

---

## 7.3 Statistical Projections: $\iff_s$

When the process realizations are observed over many cycles or across many local instances, the resulting distribution can be projected into a **Statistical Space**. This statistical projection $\iff_s$ is a representation-layer projection from lawful process structure into declared statistical observables under typed projection, observation-window, ensemble, and normalization conditions. Exclusion/addition asymmetry can motivate a central-tendency projection question, but a bell-curve or normal-like shape is not derived from $\text{RT}_{\text{core}}$ alone. Such a shape requires an explicit $F_s$ projection map, aggregation rule, and convergence or symmetry conditions.

The 049 carrier audit keeps the projection carrier distinct from the probability readout, so residue, orientation, closure, and other carrier data may vary by domain even when the statistical projection remains lawful.

**Bell-Curve Derivability Boundary (APPENDIX_F_SECTION_2_BELL_CURVE_DERIVABILITY_001):**
A normal-like projection may be admitted only as a scoped statistical projection candidate. It is invalid to infer a bell curve directly from exclusion/addition asymmetry unless the observation window or ensemble, normalization policy, aggregation rule, and convergence assumptions are declared. Skewed, heavy-tailed, multimodal, and non-convergent outputs remain admissible failure or alternative-shape classes until ruled out by explicit $F_s$ conditions.

**Skew-Condition Boundary (APPENDIX_F_SECTION_2_SKEW_CONDITIONS_001):**
Skew is treated as a statistical projection of directional imbalance, not as a direct output of $\text{RT}_{\text{core}}$. The provisional classifier is the bounded asymmetry ratio $\Omega_a$ under a declared orientation/sign convention: $\Omega_a = 1$ marks balance, $\Omega_a > 1$ marks exclusion-dominant imbalance, and $\Omega_a < 1$ marks addition-dominant imbalance. The sign and shape of projected skew remain undefined until $F_s$, the observation axis, ensemble/window, normalization policy, and aggregation rule are declared.

**Formal Block 7.3.1: Statistical Projection Relation ($\iff_s$)**
$$ D \iff_s P $$
$$ P(S_a|S_b) := F_s(D(S_a|S_b), A_{\text{adm}}, R, \text{observation\_window}) $$

**Reading:**
The observed probability of a transition is a projection of directed distinction, admissibility structure, residue support, and the chosen observation window. Probability is treated as an observer-facing projection rather than primitive causation.

**Truth Conditions (TRUTH-IFF-S-001):**
An expression $D \iff_s P$ is valid only when:
1. The source expression contains a non-zero distinction or an admissible realization trace.
2. An observation window or ensemble is declared.
3. The projection preserves trace-priority: equal probability does not imply equal process history (equal probabilities do not imply identical process lineage).
4. Probability is treated as an observer-facing projection, not primitive causation.
5. The mapping does not erase admissibility ($A_{\text{adm}}$) or residue ($R$) dependence.

**Negative Constraints:**
- $\iff_s$ is not randomness as primitive.
- $\iff_s$ is not proof that probability causes realization.
- $\iff_s$ is not identity between $D$ and $P$.

**Family Membership:**
The statistical projection relation $\iff_s$ is a statistical projection member of the parent meta-relation family schema $\langle*\rangle_x$ (the symbolic representation of the admissible relational-operator class).

**Commentary:**
In this framework, **probability is a projection**, not a primitive. The appearance of "chance" or "uncertainty" (P) arises from the observer's limited access to the full recursive state of $\mathcal{E}$ and $R$. What we perceive as a high probability transition ($P \approx 1$) is actually a state of high admissibility and strong residue support.

---

## 7.4 Example: Statistical Asymmetry

Consider a local process where the realized transitions are observed with specific frequencies.

**Example Case 7.4.1: Empirical Mapping**
- Measured Probability $P(S_1|S_2) = 0.90$
- Measured Probability $P(S_2|S_1) = 0.05$
- Inferred Metric Ratio $\Omega_a \approx 18$

---

## 7.4A Projection Domain Equivalence

A fundamental principle of the framework's measurement program is that the application projections and the relational nDOF representations are equivalent descriptions of the same underlying process state [Source: IND-CORE-ASYM-REALIZATION-001]. This is governed by the operator **Projectional Equivalence** ($\iff_m$).

**Formal Statement 7.4.2: Truth Condition for $\iff_m[I_k]$ (MPF-P1-003)**
Two expressions are projectionally equivalent with respect to a specific **procedural invariant** ($I_k$) when they preserve the same value for that invariant under projection.
$$ (A) \iff_m[I_k] (B) \iff I_k(A) = I_k(B) $$

**Governance Rule (R-INV-001):**
No invariant may be used in $\iff_m[I_k]$ unless it appears in the formal **Invariant Registry** (`registry/math/invariant_registry.json`).

**Governance Rule (R-INV-004):**
Multiple invariant claims must be listed independently rather than collapsed into a general equivalence claim. The valid form is: $(A) \iff_m[\{I_1, I_2, \dots, I_n\}] (B)$.

**Canonical Invariants (Source: MPF-P1-003):**
*   **$I_{closure}$:** Preservation of recursive closure structure.
*   **$I_{admissibility}$:** Preservation of admissible continuation condition.
*   **$I_{residue}$:** Preservation of history-conditioned continuation.
*   **$I_{orientation}$:** Preservation of orientation-reference relation.
*   **$I_{selection}$:** Preservation of selection/filtering rule.

**Commentary:**
The operator $\iff_m[I_k]$ acts as a precision bridge. It does **not** imply equality of representation ($A=B$). Rather, it signifies that both domains preserve the same "procedural fact" ($I_k$), even if their local signatures differ. Any proof of projectional equivalence must follow the **Formal Proof Template** (MPF-P1-004), requiring independent verification of each indexed invariant.

**Theorem 7.4.3: Projection Domain Equivalence (TC-003)**
Application projections and nDOF representations are projectionally equivalent because they preserve common admissibility invariants.
$$ (\mathcal{E} \neq 0_{app}) \iff_m[I_{admissibility}] (\mathcal{E} \neq 0)nDOF $$
$$ (\mathcal{E} > 0_{app}) \iff_m[I_{admissibility}] (\mathcal{E} > 0)nDOF $$

For the applied 048-049 witness family, the indexed invariants above are witness-bounded rather than universal. Closure verification and explicit projection typing are required before identity continuity may be read as preserved, and domain-sensitive carriers such as residue, orientation, scale-expression, and slot role remain outside the invariant guarantee.

---

## 7.4B Projection Signatures

A recognizable pattern of constraints, outputs, and preserved relations showing that a process expression has lawfully projected into an application-facing domain is defined as a Projection Signature ($Sig_{app}$).

**Formal Block 7.4.4: Projection Signature ($Sig_{app}$)**
$$ Sig_{app}(X) := \{ \text{source\_trace}, \text{preserved\_distinctions}, \text{projection\_operator}, \text{observable\_pattern}, \text{admissibility\_conditions} \} $$

**Reading:**
A projection is identifiable when its source trace, preserved distinctions, operator family, observable pattern, and admissibility conditions are declared. It acts as the fingerprint showing that an output belongs to a specific projection family.

**Required Fields:**
A valid projection signature must declare:
- **Source process expression:** The underlying mono-process dynamics.
- **Projection family:** The family relationship (under $\langle*\rangle_x$).
- **Preserved distinction structure:** The relational distinctions maintained.
- **Admissibility conditions:** The filters determining validity.
- **Observable output pattern:** The observer-facing presentation.
- **Forbidden identity collapse:** The explicit non-identity boundary.

**Truth Conditions (TRUTH-SIG-001):**
A projection signature $Sig_{app}(X)$ is valid only when:
1. The projection traces back to a lawful process expression.
2. The projection preserves enough distinction to remain recognizable.
3. The projection declares its operator family, such as $\iff_m$, $\iff_s$, $\iff_R$, or $\otimes$.
4. The projection does not claim identity with its source ($Sig_{app}(X) \neq X$).
5. The projection specifies the domain in which it is valid.

**Negative Constraints:**
- Projection signature is not proof of physical reality.
- Projection signature is not identity between source and output.
- Projection signature is not arbitrary resemblance.
- Projection signature does not bypass the Empirical Mapping Standards (EMS).

The 049 counterexample boundary shows that a lawful projection signature can preserve trace, admissibility, and recognizable distinctions while still allowing residue, orientation, scale-expression, or slot-role variation across domains. A valid signature therefore certifies lawful projection, not universal carrier invariance.

---

## 7.5 Missing and Provisional Formalisms

To complete the bridge between relational primitives and metric observables, the following must be induced:

1.  **Formal Definition of $\iff_m$:** [ **MISSING DEFINITION** ] How are non-scalar relational distinctions mathematically collapsed into scalar metric values?
2.  **Formal Definition of $\iff_s$:** [ **MISSING DEFINITION** ] What is the exact mapping between the intensity of mismatch $D$ and the resulting probability distribution $P$?
3.  **Role of $\Omega_a$:** [ **REQUIRES INDUCTION** ] Does $\Omega_a$ primarily function as a *classifier* of orientation (identifying which direction is preferred) or as a *predictor* (calculating the magnitude of the next re-orientation)?

---

## Summary of Chapter 7 Dependencies

- **Chapter 3** provided the $D(S_1|S_2)$ primitive.
- **Chapter 4** introduced the asymmetry domains that these metrics characterize.
- **Chapter 8** will formalize the **Floor $\epsilon$** that regularizes the calculation of $\Omega_a$.
- **Chapter 12** will examine candidate projection pathways for domains such as **matter_app** and **energy_app**, subject to the active legality and bridge-governance gates rather than assuming automatic promotion.

By distinguishing between the internal process relations and their metric/statistical projections, we preserve the "process-first" ontology of the framework while still allowing for rigorous comparison to external data.

\pagebreak

