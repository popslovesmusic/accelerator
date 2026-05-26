# Mathematical Schema (Scratch V1): Process, Admissibility, Selection, Transport, and Cross-Mechanism Agreement

**Document ID:** MS-SCRATCH-V1  
**Date:** 2026-05-25  
**Status:** schema_draft (non-canonical)  
**Evidence class:** C0 (definitions only; no new measurements)  

## 0. Scope (what this is / is not)

This document defines a **self-contained mathematical schema** for a governed recursive-process program. It introduces primitives, types, operators, equivalences, constraints, and measurement hooks sufficient to:

1. Define admissibility projection and constraint-first updates.
2. Define selection/minimization with controlled degeneracy.
3. Define null-path transport identity as a scoped property.
4. Define **cross-mechanism agreement** as a measurable condition (not an identity claim).

This schema is written **from scratch** and does **not** use any existing schema as definitional authority.

**Non-claims:**
- No theorem elevation.
- No physical ontology claim.
- No “universal” closure claims.
- No claim that discrete/continuous mechanisms are identical; only that agreement metrics can be defined and tested.

## 1. Primitive Types and Carriers

### 1.1 Process state
Let \( \mathcal{X} \) be a nonempty set called the **process state space**.

- Elements are written \(x, x', x_t \in \mathcal{X}\).
- A run is a sequence \( (x_t)_{t\in\mathbb{N}} \subseteq \mathcal{X}\).

### 1.2 Context (governance + parameters)
Let \( \mathcal{C} \) be a set of **contexts**. A context \(c\in\mathcal{C}\) may include:
- admissibility configuration,
- residue/history data,
- resolution settings,
- allowed operator family selections,
- measurement configuration.

This schema treats \(c\) as explicit input. Nothing is assumed constant unless stated.

### 1.3 Mechanism classes (representation layer)
Let \( \mathcal{M} \) be a set of **mechanism classes** (e.g., graph dynamics, cellular automata, PDE projection).

For each mechanism \(m\in\mathcal{M}\), let \( \mathcal{X}^{(m)} \) be a representation space and let
\[
\iota_m : \mathcal{X}^{(m)} \to \mathcal{X}
\]
be an interpretation map into the abstract process state space.

This enables comparing different mechanisms in \(\mathcal{X}\) without asserting they are identical in their native spaces.

## 2. Mismatch, Thresholding, and Observables

### 2.1 Mismatch functional
Let \( \mathcal{E} : \mathcal{X}\times\mathcal{C}\to \mathbb{R}_{\ge 0} \) be a **mismatch functional**.

Interpretation: \(\mathcal{E}(x;c)\) is a nonnegative scalar “pressure / deviation / non-fit” measure under context \(c\).

### 2.2 Distinguishability threshold
Let \( \theta : \mathcal{C}\to \mathbb{R}_{>0} \) be a **threshold map**.

Define the **activation predicate**
\[
\mathrm{Active}(x;c) \;:\!\iff\; \mathcal{E}(x;c) \ge \theta(c).
\]

### 2.3 Observable extraction
Let \( \mathrm{Obs} : \mathcal{X}\times\mathcal{C}\to \mathcal{O} \) be an observable extractor into an observation space \(\mathcal{O}\).

This schema does not assume \(\mathrm{Obs}\) is invertible; loss and coarse-graining are allowed.

## 3. Admissibility: Window + Projection

### 3.1 Admissibility window
Let \(A:\mathcal{C}\to \mathcal{P}(\mathcal{X})\) assign to each context \(c\) a subset \(A(c)\subseteq \mathcal{X}\), called the **admissibility window**.

Admissibility predicate:
\[
\mathrm{Adm}(x;c) \;:\!\iff\; x \in A(c).
\]

### 3.2 Admissibility projection (partial or set-valued allowed)
Define an admissibility projection operator as either:

1. **Single-valued (partial) projection:** a partial function
   \[
   \Pi_A : \mathcal{X}\times\mathcal{C} \rightharpoonup \mathcal{X}
   \]
   such that whenever \(\Pi_A(x;c)\) is defined, \(\Pi_A(x;c)\in A(c)\).

2. **Set-valued projection:** a map
   \[
   \Pi_A : \mathcal{X}\times\mathcal{C} \to \mathcal{P}(\mathcal{X})
   \]
   such that \(\Pi_A(x;c)\subseteq A(c)\).

This schema permits set-valued behavior to represent degeneracy and multi-branch admissible images.

### 3.3 Admissibility equivalence
Define an equivalence relation \(\sim_A\) on \(\mathcal{X}\) (or on a subset) such that:
- \(\sim_A\) is reflexive, symmetric, transitive.
- If \(x\sim_A y\), then \(x\) and \(y\) are treated as equivalent *for admissibility-relevant purposes* under the current governance context.

No “semantic identity” is implied; \(\sim_A\) is a governed quotient relation.

## 4. Residue / History (stateful context component)

### 4.1 Residue carrier
Let \(\mathcal{R}\) be a set of residue states.

Let \(R:\mathcal{C}\to \mathcal{R}\) extract the residue component from a context \(c\).

### 4.2 Residue update
Let \(\Psi : \mathcal{R}\times \mathcal{X}\times \mathcal{C}\to \mathcal{R}\) be a residue update rule.

This permits “memory” in admissibility/selection without requiring any specific physical interpretation.

## 5. Candidate Generation, Selection, and Update

### 5.1 Candidate set
Let \( \mathrm{Cand} : \mathcal{X}\times\mathcal{C}\to \mathcal{P}(\mathcal{X}) \) be a **candidate generator**.

Interpretation: \(\mathrm{Cand}(x;c)\) is the set of possible next states proposed before admissibility gating.

### 5.2 Selection rule (set-valued)
Let \( S : \mathcal{P}(\mathcal{X})\times\mathcal{C}\to \mathcal{P}(\mathcal{X}) \) be a selection/pruning operator.

Constraints:
- \(S(C;c)\subseteq C\).
- \(S\) may be empty even when \(C\) is nonempty (over-pruning is allowed as a failure mode).

### 5.3 Update rule (constraint-first composition)
Define the (possibly set-valued) update composition:
\[
\Delta(x;c) \;:=\; \Pi_A\!\big(S(\mathrm{Cand}(x;c);c)\,;\,c\big),
\]
interpreted with the set-valued conventions of \(\Pi_A\).

If \(\Delta(x;c)=\emptyset\), the process has **no admissible continuation** under the current context.

## 6. Transport (NavT) and Null-Path Identity (scoped)

### 6.1 Path space
Let \(\mathcal{P}\) be a set of paths (or transport programs). Let \(P_{\mathrm{null}}\in\mathcal{P}\) denote a designated null path.

### 6.2 Transport operator
Let \( \mathrm{NavT} : \mathcal{X}\times\mathcal{P}\times\mathcal{C}\to \mathcal{X} \) be a transport operator.

### 6.3 Local equivalence for transport
Let \(\sim_L\) be a local equivalence relation capturing “no meaningful change” for transport within a declared neighborhood.

### 6.4 Null-path identity property (bounded claim form)
Define the **null-path identity condition** for a specified domain \(D_{\mathrm{null}}(c)\subseteq \mathcal{X}\):
\[
\forall x\in D_{\mathrm{null}}(c): \mathrm{NavT}(x,P_{\mathrm{null}};c)\sim_L x.
\]

This is a **property to be checked** under explicit domain constraints; it is not asserted globally by schema alone.

## 7. Orientation, Reference Classes, and Minimizer Switching

### 7.1 Orientation space and admissible orientation window
Let \(\Omega\) be an orientation space. Let \(W_{\mathrm{adm}}:\mathcal{C}\to \mathcal{P}(\Omega)\) be an admissible orientation window.

### 7.2 Orientation-conditioned mismatch
Define an orientation-conditioned mismatch:
\[
\mathcal{E}_\Omega : \Omega\times\mathcal{X}\times\mathcal{C}\to \mathbb{R}_{\ge 0}.
\]

Interpretation: \(\mathcal{E}_\Omega(\omega,x;c)\) measures mismatch of orientation choice \(\omega\) in state \(x\) under context \(c\).

### 7.3 Set-valued minimizer map (degeneracy allowed)
Define the set of minimizers:
\[
O^*(x;c) \;:=\; \operatorname{argmin}_{\omega\in W_{\mathrm{adm}}(c)} \mathcal{E}_\Omega(\omega,x;c)
\subseteq \Omega.
\]

If \(O^*(x;c)\) has cardinality \(>1\), degeneracy is present.

### 7.4 Reference map and equivalence
Let \(\mathrm{Ref}:\Omega\times\mathcal{C}\to \mathcal{K}\) map orientations into a reference-class carrier \(\mathcal{K}\).

Define \(\omega_1 \sim_{\mathrm{Ref}} \omega_2\) iff \(\mathrm{Ref}(\omega_1;c)=\mathrm{Ref}(\omega_2;c)\).

### 7.5 Switching event and bounded stability condition
Given two successive selections \(\omega_t\in O^*(x_t;c)\) and \(\omega_{t+1}\in O^*(x_{t+1};c)\), define a switching event when \(\omega_{t+1}\not\sim_{\mathrm{Ref}} \omega_t\).

A bounded “switching stability” predicate can then be expressed as a conjunction of:
- admissibility preservation of orientation (\(\omega_{t+1}\in W_{\mathrm{adm}}(c)\)),
- bounded mismatch change (\(|\mathcal{E}_\Omega(\omega_{t+1},x_{t+1};c)-\mathcal{E}_\Omega(\omega_t,x_t;c)| \le \theta_\Omega(c)\) for some governance threshold \(\theta_\Omega\)),
- and/or “declared boundary crossing” (a governed event label indicating a permitted regime transition).

This schema intentionally does not force a single definition of “declared boundary crossing”; it must be defined by the governed campaign or rulepack.

## 8. Cross-Mechanism Agreement (measurement layer)

### 8.1 Comparable observation space
To compare mechanisms \(m_1, m_2\), define a shared measurement map:
\[
\mathrm{Meas} : \mathcal{X}\times\mathcal{C}\to \mathbb{R}^d,
\]
and compute comparable traces \(y^{(m)}_t := \mathrm{Meas}(\iota_m(x^{(m)}_t);c)\).

### 8.2 Agreement metric (example family)
Define an agreement metric:
\[
\mathrm{Agree}(m_1,m_2;c)\in[0,1]
\]
constructed from the traces \(y^{(m_1)}\) and \(y^{(m_2)}\) via a declared scoring rule (correlation, classification agreement, event-set overlap, etc.).

This schema treats the specific scoring rule as part of governance \(c\) (so it is auditable and change-controlled).

### 8.3 FV-4 style schism predicate (bounded)
Define a schism predicate:
\[
\mathrm{Schism}(m_1,m_2;c) :\!\iff \mathrm{Agree}(m_1,m_2;c) < \tau(c)
\]
for a declared tolerance \(\tau(c)\in(0,1)\).

Schism is a **measurement outcome**, not a global refutation of the entire schema.

## 9. Minimal Failure Taxonomy (schema-local)

This is a schema-local classification of failure sources for audits and does not supersede any repository-wide taxonomy.

- **Boundary collapse:** \(A(c)=\emptyset\) or \(\Pi_A\) becomes undefined/empty in the intended domain.
- **Residue instability:** \(\Psi\) causes drift that invalidates invariance assumptions required for stability arguments.
- **Projection instability:** \(\mathrm{Obs}\) or \(\mathrm{Meas}\) hides divergences (agreement “looks good” while state-level divergence grows).
- **Hidden coupling:** agreement depends on an undeclared shared parameter, seed coupling, or synchronized random stream.
- **Implementation artifact:** agreement/failure is caused by implementation choices rather than the operator constraints the campaign purports to test.
- **Theorem overreach:** a bounded/conditional stability property is described as unconditional closure.

## 10. Operationalization Checklist (what must be pinned by a campaign)

Any campaign claiming to test minimizer switching stability across mechanisms must explicitly declare:

1. Mechanism set \( \mathcal{M}_{\mathrm{test}} \subseteq \mathcal{M}\).
2. Interpretation maps \(\iota_m\) or a documented surrogate comparison method.
3. Measurement map \(\mathrm{Meas}\) and agreement definition \(\mathrm{Agree}\).
4. Threshold/tolerance \(\tau(c)\) and which metric(s) constitute failure.
5. Domain restrictions \(D(c)\subseteq \mathcal{X}\) (or test distribution over \(\mathcal{X}\)).
6. Degeneracy handling rule (how set-valued \(O^*\) is resolved for tracing).
7. Seed policy and independence guarantees.

## 11. What this schema does NOT grant
- It does not grant C6 status to any claim.
- It does not license “mechanism independence” statements without an explicit agreement metric and tolerance.
- It does not resolve FV-4; it only makes the failure mode representable in the math.

## Appendix A: Symbol Index
- \(\mathcal{X}\): abstract process state space  
- \(c\in\mathcal{C}\): governance context  
- \(m\in\mathcal{M}\): mechanism class  
- \(\iota_m\): interpretation map into \(\mathcal{X}\)  
- \(\mathcal{E}\): mismatch functional; \(\theta\): threshold  
- \(A(c)\): admissibility window; \(\Pi_A\): admissibility projection  
- \(\sim_A, \sim_L, \sim_{\mathrm{Ref}}\): governed equivalences  
- \(\Psi\): residue update  
- \(\mathrm{Cand}\): candidate generator; \(S\): selector; \(\Delta\): update composition  
- \(\mathrm{NavT}\): transport; \(P_{\mathrm{null}}\): null path  
- \(\Omega\): orientation space; \(W_{\mathrm{adm}}\): admissible orientation window  
- \(O^*\): set of minimizers; \(\mathrm{Ref}\): reference-class map  
- \(\mathrm{Meas}\): measurement map; \(\mathrm{Agree}\): agreement metric; \(\tau\): tolerance  

