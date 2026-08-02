# Independent Orientation-Resolution Fixture Report

## Result

`PASS_BOUNDED_FIXTURES`: 5 fixtures passed and 0 failed.

## Covered Boundaries

- Inadmissible candidates are removed before comparison.
- Higher admissible scores win.
- Equal scores use a stable canonical-key tie-breaker.
- Reversing discovery order produces the same result.
- No admissible candidate returns an explicit unresolved outcome.

## Interpretation

The candidate evaluator demonstrates deterministic behavior under its explicit fixture rules. It does not define canonical orientation semantics, prove MTO determinism, establish RT identity, or authorize promotion.

The MTO/OTM source remains `NOT_REVIEWED`, `HOLD_C1`, and `NON_CANONICAL_CANDIDATE`.
