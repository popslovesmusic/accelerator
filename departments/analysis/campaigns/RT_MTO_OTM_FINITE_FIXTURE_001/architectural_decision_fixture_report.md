# Bounded Architectural Decision Fixture Report

## Result

`PASS_BOUNDED_ARCHITECTURAL_FIXTURES`: all 12 required fixture classes passed with 0 failures.

## Decisions Exercised

- Explicit Aspect context is required.
- Multiple MTO results are preserved unless a registered selector is present.
- Noncanonical single-result selection is rejected.
- Primitive multiplicity is preserved.
- Canonical orientation keys are separated from runtime-derived keys.
- Semantic ties are preserved.
- Matching outputs are classified as output-equivalent only.
- RT equivalence remains undetermined without a registered profile.

## Boundary

These results implement the bounded architectural decision packet as a fixture contract. They do not establish universal RT semantics, mathematical closure, global aspect equivalence, universal MTO uniqueness, or universal OTM recoverability.
