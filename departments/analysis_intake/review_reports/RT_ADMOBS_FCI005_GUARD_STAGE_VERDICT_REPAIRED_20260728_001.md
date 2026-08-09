# Repaired Three-Way FCI-005 Evaluator

The structural witness no longer requires a passing threshold, so both `PAIR_PASS` and `PAIR_FAIL` are reachable.

`ThresholdMapResult_x` explicitly distinguishes `VALID`, `INVALID`, and `UNDEFINED`. `BridgeVerdictInvariant_x` quantifies over final per-witness pair verdicts, not merely preservation outcomes.

The binary evaluator returns `COMPATIBLE`, `INCOMPATIBLE`, or `UNDEFINED`. Pairwise aggregation preserves this distinction: any definite incompatibility dominates, otherwise an undefined evaluator yields an undefined aggregate rather than a false result.

This is definition-level provisional evidence only. `BCon_x` remains unbound, `H_x` remains undeclared, and `delta_a` is unchanged.
