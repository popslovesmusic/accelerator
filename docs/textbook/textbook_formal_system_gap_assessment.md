# Textbook Formal System Gap Assessment

**Scope**
This note records what pieces are still needed for `mono_process_textbook_complete.md` to qualify as a formal mathematical system rather than a partially formalized research program.

**Directly observed in the textbook**
- The draft already contains an axiomatic floor: `(\mathcal{E} \neq 0) \iff_R \delta_a(\mathcal{E} > 0)`.
- The draft already contains a growing primitive vocabulary: `\mathcal{E}`, `S`, `T`, `D`, `R`, `\Psi`, `\delta_a`, `\iff_R`, `\iff_x`, `\otimes`, `\Omega_a`.
- The draft already contains operator and symbol registries in the appendices.
- The draft already contains an explicit missing-definition ledger in Appendix F.
- The draft already contains governance for claim levels, review locks, and dependency propagation.

**Inferred inside the framework**
The current textbook is close to a formal system in structure, but it is not yet a closed formal calculus. The main missing pieces are below.

## 1. Syntax Closure

The textbook uses formulas, but it does not yet fully specify a grammar for well-formed expressions.

Minimum missing pieces:
- A declaration of object classes: states, residues, contexts, operators, relations, projections.
- A rule for what counts as a term.
- A rule for what counts as a well-formed formula.
- A rule for typing subscripts such as `_R`, `_x`, `_a`, `_app`, and context labels.
- A rule distinguishing object-language expressions from commentary and governance labels.

## 2. Semantic Closure

Many primitives have partial operational descriptions but not full interpretation clauses.

Minimum missing pieces:
- Exact interpretation of `\iff_R`.
- Exact interpretation of `\delta_a`.
- Exact interpretation of `\iff_x`.
- Exact interpretation of `R_{\leftrightarrow}` versus `\leftrightarrow_R`.
- Exact interpretation of `0-state`.
- Exact interpretation of `\otimes` and `\iff_s`.

This is visible in the textbook's own placeholders and in Appendix F.

## 3. Truth Conditions

The system still needs explicit truth conditions for its core relational statements.

Minimum missing pieces:
- When is `(A \leftrightarrow_R B) = True`?
- When does residue-conditioned closure fail?
- What formally produces `0-state`?
- What conditions make a coupling statement valid, invalid, or undecidable?
- Which statements are definitional, and which are empirical or model-relative?

Without these, the notation remains interpretable but not evaluable.

## 4. Inference Rules

The textbook contains axioms and candidate operators, but it does not yet define a proof calculus.

Minimum missing pieces:
- Substitution rules.
- Introduction and elimination rules for major operators.
- Update rules governing `\Psi`, `\delta_a`, and residue-conditioned transitions.
- Rules for moving between relation-level statements and projection-level statements.
- Conditions under which one theorem depends on, or may be derived from, another.

Without inference rules, the system can describe claims but cannot rigorously derive them.

## 5. Operator Algebra

The operator family exists more as a registry than as a fully defined algebra.

Minimum missing pieces:
- Composition rules.
- Associativity or explicit non-associativity.
- Symmetry or directionality conditions.
- Identity elements, if any.
- Collapse or incompatibility rules.
- Reduction rules showing when one operator can be rewritten into another.

This requirement is already implied by the Algebraic Stability section of Appendix C.

## 6. Model Class

The textbook still needs at least one explicit class of mathematical structures in which its statements are interpreted.

Minimum missing pieces:
- What kind of structure interprets `S`?
- What kind of structure interprets `R`?
- Is `D` scalar-valued, order-valued, lattice-valued, or something else?
- Is admissibility set-based, order-theoretic, graph-theoretic, or categorical?
- What counts as a valid model of the primary axiom?

Without a model class, consistency and satisfiability remain unclear.

## 7. Boundary and Failure Conditions

The textbook is strong on governance, but the mathematical side still needs sharper internal failure criteria.

Minimum missing pieces:
- Formal decoupling condition.
- Formal collapse condition.
- Conditions for undefined expressions.
- Conditions for operator misuse across incompatible types.
- Counterexamples and non-examples for major claims.

This is necessary to keep the system falsifiable and non-circular.

## 8. Separation of Layers

The draft currently mixes several layers:
- formal mathematical statements
- explanatory commentary
- governance status
- simulation evidence references
- application projections

A formal system can contain all of these, but they should be cleanly separated.

Minimum missing pieces:
- a strict core calculus layer
- a model layer
- a projection/application layer
- a governance/evidence layer

That separation would make proofs cleaner and prevent status labels from being mistaken for derivations.

**External resemblance (analogy only)**
The missing pieces are the same kinds of pieces expected in ordinary formal systems: grammar, semantics, inference, models, and failure conditions. This is a structural comparison only, not a claim that the present textbook already meets those standards.

**What this does not prove**
- It does not prove the Mono-Process Framework is false.
- It does not prove the textbook cannot become formal.
- It does not prove any current operator is invalid.
- It does not prove the application chapters fail as research scaffolds.

**Failure modes / uncertainty**
- Some of the missing pieces may already exist in upstream notes but are not yet canonically integrated into the textbook.
- Some operators may need to be narrowed rather than expanded to become formally tractable.
- Some application-facing chapters may need to be downgraded to model-relative language until the core calculus is closed.

## Minimum path to formal-system status

1. Freeze a core typed grammar.
2. Define the semantics of the primary operators.
3. State explicit truth conditions for closure, decoupling, and zero-state.
4. Publish a small inference rule set.
5. Give at least one concrete model and one countermodel family.
6. Separate core calculus from governance and application material.

**Working conclusion**
`mono_process_textbook_complete.md` already contains the skeleton of a formal system. The remaining work is not primarily conceptual expansion. It is semantic closure, proof-rule definition, operator algebra, and explicit model construction.
