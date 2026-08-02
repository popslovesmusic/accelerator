# Independent MTO/OTM Cross-Validation Report

## Result

`PASS_CROSS_VALIDATED_FIXTURES`: 6 independent checks passed and 0 failed.

## Agreement Checks

- Candidate RT identity matched.
- MTO input permutation produced the same candidate output.
- Role-mismatch rejection matched.
- OTM primitive multiplicity was preserved.
- Orientation tie-breaking was independent of input order.
- No-admissible-candidate behavior matched.

## Limits

The second implementation independently reproduces the provisional fixture contract. This is bounded cross-validation only; it does not establish canonical MTO/OTM semantics, RT equivalence, universal closure, or theorem status.
