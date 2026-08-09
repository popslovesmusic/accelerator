# RT Orientation and Boundary-Coupling Interface Contracts

**Status:** C1 model-relative formalization candidate  
**Source:** `RT_ORIENTATION_BOUNDARY_COUPLING_JOINT_REVIEW_20260802_001`  
**Scope:** bounded definitions and interface contracts only  
**Promotion:** not authorized

## 1. Scope

This note formalizes the bounded interfaces identified in the joint review of contextual RT roles and boundary-only coupling/internal propagation. It does not define a physical hexahedron, sphere, byte machine, thermodynamic density, or external ontology. It does not modify an existing lemma or proof.

The contracts are intended to make later finite fixtures possible while preserving the distinction between:

- RT identity and contextual role;
- boundary coupling and internal propagation;
- ordered computational representation and ontology; and
- orientation-field output and downstream scalar estimation.

## 2. Declared domains

Let \(P\) be a declared working proposition and \(R\) a bounded RT continuation. Define the contextual role function:

\[
\operatorname{role}_P(R)\in
\{\operatorname{root},\operatorname{aspect},\operatorname{closed},\operatorname{primitive}\}.
\]

The role is proposition-relative. It does not create a new object identity:

\[
\operatorname{id}(R,P)=\operatorname{id}(R,P')=R
\]

whenever the same RT is observed under different propositions. This is a model contract for identity preservation, not a proof of an external identity principle.

## 3. Contextual role and primitive sufficiency

Let \(\operatorname{closed}(R,P)\) indicate that the RT has a bounded closure representation under proposition \(P\). Let \(\operatorname{sufficient}(R,P)\) indicate that evaluating \(R\) at the current resolution is enough to decide the declared proposition without opening an unresolved child.

The contextual primitive predicate is:

\[
\operatorname{primitive}_P(R)
\;:\Longleftrightarrow\;
\operatorname{closed}(R,P)\land\operatorname{sufficient}(R,P).
\]

The decomposition rule is fail-closed:

\[
\neg\operatorname{primitive}_P(R)
\;\Rightarrow\;
\operatorname{decompose}(R,P),
\]

provided an admissible child decomposition exists. If no admissible decomposition is available, the result is `UNRESOLVED`, not an inferred primitive.

The stopping rule is therefore contextual and finite:

\[
\operatorname{stop}(R,P)
\;\Longleftrightarrow\;
\operatorname{primitive}_P(R).
\]

The contract does not yet provide a decision algorithm for `sufficient`; that remains a fixture and validation obligation.

## 4. Primitive evaluation and orientation field

Evaluation returns an orientation-field value, not a scalar sign:

\[
\operatorname{eval}_P(R)
\to
\mathcal O_P(R),
\]

where \(\mathcal O_P(R)\) is an ordered field record. The labels `+` and `−` may be used as non-scalar placeholders:

\[
\operatorname{class}_P(R)\in\{+, -, \operatorname{UNRESOLVED}\},
\]

but `+` and `−` do not carry magnitude, probability, angle, or arithmetic value. Any angular or scalar estimate is a downstream map:

\[
\operatorname{estimate}_P:
\mathcal O_P(R)\to\mathcal V_P,
\]

and is not interchangeable with the primitive evaluation.

## 5. Ordered byte-array interface

The computational surface is modeled as an ordered byte sequence:

\[
B=(b_0,b_1,\ldots,b_{n-1}),
\qquad b_i\in\{0,\ldots,255\}.
\]

Each byte has an explicitly declared bit order. A representation is not valid unless it declares:

1. byte-index order;
2. bit-index order within each byte;
3. child-RT association for each addressable segment;
4. the active proposition and orientation context; and
5. the allowed reorganization operation.

The order-preservation contract is:

\[
\operatorname{reorder}(B,\pi)\text{ is admissible only if }\pi
\text{ is declared by the proposition and preserves the declared trace.}
\]

An arbitrary permutation is rejected as `ORDER_UNDEFINED`; it must not be silently treated as a matrix equivalence. The byte array remains a computational representation and does not become the RT ontology.

## 6. Boundary coupling and no-transport

For two RTs \(R_1,R_2\), define boundary interfaces \(\partial R_1\) and \(\partial R_2\). Coupling is a boundary relation:

\[
\operatorname{couple}_P(R_1,R_2)
\subseteq
\partial R_1\times\partial R_2.
\]

An admissible coupling produces a boundary-condition update:

\[
\operatorname{couple}_P(R_1,R_2)
\to
\Delta\operatorname{BC}_{1,2}.
\]

The no-transport invariant is:

\[
\operatorname{interior}(R_1)\not\to\operatorname{interior}(R_2)
\quad\text{and}\quad
\operatorname{interior}(R_2)\not\to\operatorname{interior}(R_1)
\]

as a direct coupling result. Only boundary conditions are exchanged by the coupling interface. A fixture that records direct interior transfer fails the contract.

## 7. Reference alignment and internal propagation

Reference alignment translates the boundary update into an internal condition:

\[
\operatorname{align}_P(\Delta\operatorname{BC}_{1,2},R_i)
\to
\Delta\operatorname{Ref}_i.
\]

Internal propagation is then a lawful continuation over the RT’s own organization:

\[
\operatorname{propagate}_P(R_i,\Delta\operatorname{Ref}_i)
\to
R_i'.
\]

Propagation is not a transport edge between RTs. It is an intra-RT update whose admissibility must be evaluated against the current proposition and residue. The minimum separation contract is:

\[
\operatorname{couple}(R_1,R_2)\ne\operatorname{propagate}(R_1,R_2).
\]

The second expression is undefined under this interface because propagation has one RT as its organized carrier.

## 8. Recursive closure

Let \(C_P\) be the closure operator. For an ordered child sequence \(R_{1:n}\) and their orientation fields \(\mathcal O_{1:n}\):

\[
C_P((R_1,\mathcal O_1),\ldots,(R_n,\mathcal O_n))
\to
(R,\mathcal O_R).
\]

The operator must preserve:

- child order;
- source proposition;
- identity/provenance links;
- unresolved status where a child is not sufficient; and
- the distinction between field aggregation and scalar estimation.

Closure may be applied recursively only when the parent composition contract is satisfied. A child marked `UNRESOLVED` cannot be silently converted into a primitive or a closed parent.

## 9. End-to-end bounded transition

The combined interface is:

\[
\begin{aligned}
&\operatorname{couple}_P(R_1,R_2)
\to\Delta\operatorname{BC}_{1,2}
\to\Delta\operatorname{Ref}_i\\
&\to\operatorname{propagate}_P(R_i,\Delta\operatorname{Ref}_i)
\to R_i'
\to\operatorname{eval}_P(R_i')
\to\mathcal O_P(R_i')\\
&\to C_P(\mathcal O_{children})
\to\mathcal O_P(R_i')
\to\operatorname{estimate}_P(\mathcal O_P(R_i')).
\end{aligned}
\]

This sequence separates boundary interaction, reference alignment, internal continuation, ordered representation, recursive closure, and downstream estimation. It is a bounded procedural contract, not a physical model.

## 10. Required finite fixtures

The next validation package should include at least:

1. role reclassification under two propositions with invariant RT identity;
2. primitive sufficiency and unresolved-child rejection;
3. byte-order and bit-order permutation rejection;
4. direct interior-transfer rejection;
5. boundary update followed by internal-only propagation;
6. closure order preservation; and
7. rejection of scalar/angle use at primitive evaluation.

## 11. Status and limitations

These contracts are C1 model-relative candidates. They do not prove a theorem, derive physical geometry, establish thermodynamic conservation, or validate the hexahedron/sphere analogy. Independent review and finite fixtures are required before any stronger claim is considered.
