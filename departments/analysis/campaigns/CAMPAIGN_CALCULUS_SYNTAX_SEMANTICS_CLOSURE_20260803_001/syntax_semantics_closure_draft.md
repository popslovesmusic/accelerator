# Syntax and Semantics Closure Work Package

## Scope

This is a noncanonical analysis draft responding to the calculus-completeness crawl. It is a work package, not a promoted mathematical source.

## Closure target

The target chain is:

`grammar → typed expressions → semantic interpretation → truth conditions → explicit model → reproducible evaluation`.

The package must not begin with theorem promotion or bridge expansion.

## Deliverable 1: typed syntax

Declare lexical categories for:

- constants and variables;
- states, residues, contexts, domains, and projections;
- relations and relation qualifiers;
- operators and operator applications;
- formulas and guarded continuation expressions.

Every subscript and context marker must have a declared type. Commentary, governance labels, evidence classes, and application names must remain outside the object language unless explicitly reintroduced as typed symbols.

## Deliverable 2: formation rules

Define formation judgments of the form `Γ ⊢ e : T` and `Γ ⊢ φ : Prop`. Include binding, substitution, context compatibility, relation arity, partial-operator failure, and invalid-expression classification. No expression should be accepted merely because it is visually present in the textbook.

## Deliverable 3: semantics

Declare a model tuple containing at minimum domains for process states, residues, contexts, admissibility, relations, and projections. Each core operator needs an interpretation function or an explicit deferred status. `iff_R`, `delta_a`, `iff_x`, coupling, closure, zero-state, and partial composition are priority targets.

## Deliverable 4: truth conditions

Specify when a relation is true, false, or undecidable within the model. Specify closure failure, decoupling, empty admissibility, typed-zero loss, and unresolved partial-normal-form outcomes. Truth conditions must not be inferred from simulation success.

## Deliverable 5: model class

Start with one finite relational model class so parsing and evaluation are executable. The finite model is a test domain, not a claim that the framework is finite in general. Record satisfiability, countermodels, and model-class limitations.

## Validation and falsification

Required checks are parser determinism, type-checker determinism, substitution preservation, semantic totality or explicit partiality, truth-condition reproducibility, countermodel coverage, and independent reviewer reconstruction. Failure of any required check keeps the package noncanonical.

## Proof boundary

Successful parsing or finite-model evaluation does not establish consistency, completeness, soundness, confluence, termination, or external validity. Those remain separate proof obligations.

## Next handoff

The next specialist should produce the frozen grammar and typed abstract-syntax schema first. No downstream semantic or algebraic closure work should be treated as complete until that artifact is reviewed.
