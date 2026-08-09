# Technical Note — Relational Operator Register
## Mono-Process Framework | Relational Notation Consolidation

**ID:** MPF-TN-OPER-2026-05-28-V0.1
**Status:** Draft / Working Consolidation
**Compliance:** Charter-aligned draft. All claims provisional. No physics equivalence asserted.
**Sources consolidated:** Relational Notation Recap, MONO_PROCESS_MATHEMATICAL_SCHEMA_V1.6, TN Relational Notation and Procedural Quantity States

---

## 0. Purpose

This technote consolidates relational operator definitions, resolves notation inconsistencies identified across working documents, and establishes a canonical operator register for the MPF relational notation system.

The notation system functions as a **procedural interpretation layer** — not a replacement for conventional mathematics, and not a claim of physical unification.

---

## 1. Foundational Pre-Condition

**All operators in this register presuppose:**

$$(\mathcal{E} \neq 0)$$

If distinguishability collapses to zero, no coupling subscript is well-formed and no operator in this register is active. This is not merely the first axiom — it is the **condition of possibility for the entire operator grammar**.

### 1.1 State vs Condition — A Critical Distinction

These two expressions are not equivalent:

| Expression | Meaning |
|---|---|
| $(\mathcal{E})$ | The underlying procedural state/value itself |
| $(\mathcal{E} \neq 0)$ | A condition asserted about that state — non-zero participation |

The condition $(\mathcal{E} \neq 0)$ does not merely participate in coupling expressions as a left-hand term. It **populates the subscript position of the coupling operator itself**. That is:

$$\Leftrightarrow_{\mathcal{E}}$$

means the distinguishability condition is the admissibility condition governing the coupling — not a separate entity being coupled. This is the foundational operator-generation mechanism.

---

## 2. Positional Grammar — Coupling vs Decoupling

The relational notation uses **subscript position** to distinguish coupling from decoupling:

| Form | Family | Role |
|---|---|---|
| $\Leftrightarrow_x$ | Coupling | $x$ conditions the coupling act |
| $x_\Leftrightarrow$ | Decoupling | $x$ conditions the decoupling act |

This positional convention is consistent across all operator families. The symbol $\Leftrightarrow$ retains its reciprocal closure topology in both positions; the subscript location encodes directionality of the process event.

A full couple → decouple → recouple cycle is expressible as:

$$\Leftrightarrow_{xa} \;\rightarrow\; a_\Leftrightarrow \;\rightarrow\; \Leftrightarrow_{xa}$$

---

## 3. Canonical Operator Register

### 3.1 Coupling Operators $(\Leftrightarrow_x)$

| Operator | Name | Definition | Notes |
|---|---|---|---|
| $\Leftrightarrow_R$ | Residue-conditioned coupling | Reciprocal coupling conditioned by accumulated residue history | Primary operator in NOT-Axiom |
| $\Leftrightarrow_{xa}$ | Admissibility-conditioned coupling | Reciprocal coupling conditioned by admissibility window $A$ | Active interaction operator |
| $\Leftrightarrow_{xb}$ | Cross-basin projection coupling | Reciprocal coupling conditioned by cross-basin projection | Requires prior stabilization — see 3.3 |
| $\Leftrightarrow_{\mathcal{E}}$ | Distinguishability-conditioned coupling | $\mathcal{E} \neq 0$ populates the subscript; distinguishability is the coupling condition | Foundational; see Section 1.1 |
| $\Leftrightarrow_\Omega$ | Orientation-driven coupling | Coupling driven by orientation array $I = \{-(i)_\alpha\}$ | Appears in stabilization composition |
| $\Leftrightarrow_K$ | Lock-state coupling | Stabilized fixed-point coupling; output of stabilization composition | Terminal coupling state |

### 3.2 Decoupling Operators $(x_\Leftrightarrow)$

| Operator | Name | Definition | Notes |
|---|---|---|---|
| $R_\Leftrightarrow$ | Residue-conditioned decoupling | Decoupling conditioned by residue history | Inverse process to $\Leftrightarrow_R$ |
| $a_\Leftrightarrow$ | Admissibility-conditioned decoupling | Decoupling conditioned by admissibility window | Inverse process to $\Leftrightarrow_{xa}$ |
| $b_\Leftrightarrow$ | Cross-basin decoupling | Decoupling conditioned by cross-basin projection | Inverse process to $\Leftrightarrow_{xb}$ |
| $K_\Leftrightarrow$ | Lock-breaking decoupling | Decoupling from stabilized lock state | Requires sufficient $P_\Delta$ or mismatch threshold |

### 3.3 Composition Behavior

| Composition | Result | Interpretation |
|---|---|---|
| $\Leftrightarrow_{xa} \circ \Leftrightarrow_{xa}$ | Admissibility saturation | Repeated admissibility-conditioned coupling converges to fixed point |
| $\Leftrightarrow_{xa} \circ \Leftrightarrow_\Omega$ | $\Leftrightarrow_K$ | Interaction + Orientation = Lock |
| $\Leftrightarrow_{xb} \circ (\neg \Leftrightarrow_K)$ | $\varnothing$ | Cross-basin projection requires prior stabilization |

**Note on idempotence:** The saturation behavior (first row above) is a *property* of $\Leftrightarrow_{xa}$ under repeated composition, not a separate operator. The symbol $\Leftrightarrow_a$ used in earlier drafts is retired; saturation is expressed as a convergence theorem over $\Leftrightarrow_{xa}$.

---

## 4. Directional Operators

These are not coupling operators but appear in the operator grammar:

| Operator | Meaning |
|---|---|
| $\rightarrow_R$ | Directional relation conditioned by residue |
| $\prec$ | Procedural ordering (replaces universal time) |
| $\mapsto$ | Projection — procedural state projects to scalar observable |
| $\delta_a$ | Admissibility-constrained continuation/update operator |

---

## 5. Regime Labels

The suffix $_{app}$ denotes **interpretive regime**, not physical equivalence.

| Label | Procedural Interpretation |
|---|---|
| $QM_{app}$ | Local admissibility dynamics; probabilistic continuation structure; fine-grained recursive variation |
| $GR_{app}$ | Large-scale statistical continuation geometry; stabilized aggregate structure; macroscopic process topology |
| $\text{time}_{app}$ | Emergent ordering of continuation density across $I$ |
| $\text{gravity}_{app}$ | $P_\Delta$ deformation of global arbitration topology |
| $\text{weak}_{app}$ | $P_\Delta$ discharge via transformation |
| $\text{strong}_{app}$ | $P_\Delta$ internalization via triadic confinement |

---

## 6. Symbol Collision Resolutions

The following collisions were identified across source documents and are resolved here:

| Symbol | Collision | Resolution |
|---|---|---|
| $\alpha$ | Used as basin index in $I = \{-(i)_\alpha\}$ AND as coupling channel in $\Leftrightarrow_{x\alpha}$ | Reserved exclusively for basin index. Coupling channel expressed via named subscripts $xa$, $xb$, $R$, $\mathcal{E}$ |
| $\Leftrightarrow_a$ | Appeared in idempotence axiom without standalone definition | Retired. Behavior promoted to saturation property of $\Leftrightarrow_{xa}$ |
| $\Leftrightarrow_{x\alpha}$ | Generic working form in notation recap; ambiguous with $\Leftrightarrow_{xa}$ | Retired as standalone operator. Replaced by specific named operators in Section 3 |

---

## 7. Procedural Quantity States

For completeness, the quantity state notation used alongside operators:

| Expression | Meaning |
|---|---|
| $6$ | Scalar form — observable projection |
| $(6)_{nDOF}$ | Procedural quantity state — $n$ admissible continuation degrees of freedom |
| $(6)_{nDOF} \mapsto 6$ | Projection relation — procedural state reduces to scalar observable |
| $(6)_{nDOF}\delta$ | Procedural quantity state with admissibility-constrained continuation active |

Different procedural states may project to the same scalar while possessing distinct continuation behaviors internally.

---

## 8. Collapse / Null Conditions

| Condition | Expression | Meaning |
|---|---|---|
| Admissibility collapse | $D_{rel} > W_{adm} \Rightarrow \varnothing_{coupling}$ | Mismatch exceeds admissibility window; coupling fails |
| Realization failure | $\neg[(\mathcal{E} \neq 0) \Leftrightarrow_R \delta_a(\mathcal{E} > 0)]$ | NOT-Axiom fails to propagate |
| Symmetry fracture | $D(S_1 \mid S_2) = (S_2 \mid S_1)^D$ | Asymmetry collapses; relational pressure goes to zero |
| Zero-state | $\mathcal{E} = 0$ | No subscript populatable; entire operator grammar inactive |

---

## 9. Open Items

The following require formalization before this register reaches endorsed status:

1. **Statistical characterization** — process states are described as statistically characterizable (continuation tendencies, admissibility distributions, transition likelihoods) but no formal measure or sample space has been defined.
2. **$K_\Leftrightarrow$ threshold** — lock-breaking decoupling is named but the conditions under which it activates are not yet specified beyond "sufficient $P_\Delta$ or mismatch."
3. **$\Leftrightarrow_\Omega$ standalone definition** — orientation-driven coupling appears only in the composition axiom; a standalone definition is needed.
4. **Procedural flow as named object** — the chain `distinction → admissibility filter → continuation → residue inscription → orientation → stabilization → projection → geometry_app` from V1.6 Section 1 deserves promotion to a numbered definition.

---

**Authority:** Mono-Process Framework Math Program.
**Next review:** Pending Gap resolution and registry verification. ∎
