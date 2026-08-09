# Adversarial MTO/OTM Counterexample Report

## Result

Five finite boundary counterexamples were found. The result is `COUNTEREXAMPLES_FOUND_BOUNDARY_REOPENED`.

## Findings

- Context must be explicit when the same primitive organization can be used in different roles.
- Set-only OTM decomposition collapses distinct multiplicities.
- Duplicate orientation tie keys cannot produce a deterministic selection.
- Multiple MTO outputs for one input violate single-valued deterministic selection.
- Equal observed outputs do not establish equivalence of distinct aspect organizations.

## Consequence

The provisional model must retain context-indexed semantics, multiplicity, unique canonical tie keys, single-valued MTO selection, and a strict separation between output matching and operand equivalence.

These are finite candidate counterexamples, not counterexamples to canonical RT mathematics. The source remains noncanonical and requires human review.
