# Adversarial Countermodels for Intake Proposals

## Scope

This C1 campaign tests the finite candidate semantics used for intake entries 056, 057, and 060. Campaign 059’s existing counterexample suite remains authoritative for its bounded fixture package.

## Directly observed/defined

Eight counterexamples were found in ten adversarial cases:

- 056: boundary exclusion semantics are non-unique; empty admissible families and boundary-free orientations are possible.
- 057: scalar projection and context removal collapse distinct typed orientations; self-inverse orientations require an explicit exception.
- 060: MTO can be nondeterministic, aspect histories can collapse, recursive cycles can prevent termination, and set-valued OTM can erase multiplicity.

## Inferred inside framework

The proposals require additional semantic obligations before general validation: frozen exclusion semantics, explicit failure classes, typed context, MTO selection/tie-breaking, well-founded recursion, and multiplicity-preserving OTM output where required.

## External resemblance (Analogy only)

These failure modes resemble ambiguity in operational semantics, quotient identity loss, nondeterministic rewriting, and non-well-founded recursion. These are analogies only.

## What it does NOT prove

The countermodels do not falsify every possible formulation of the intake proposals. They falsify or constrain the particular finite candidate semantics tested here.

## Failure modes / uncertainty

The suite is finite and intentionally adversarial. It identifies obligations and boundaries; it does not search the full space of alternative definitions.

## Status

The entries remain C1 and `HOLD_C1`. No promotion is justified. The next required work is to define and test repaired semantics for each exposed obligation, with counterexamples retained.
