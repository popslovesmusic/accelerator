# Repaired FCI-005 Pretest Candidate

The pretest candidate now uses a three-valued `ThresholdBridgeResult_x`: `PRESERVED`, `NOT_PRESERVED`, or `UNDEFINED`. Undefined threshold comparisons are not coerced to rejection.

Source witnesses are retained through `BridgeWitnessRecord_x`, with permitted-witness provenance and `BridgeVerdictInvariant_x`. Nonfunctional witness mappings must produce a stable verdict across all permitted witnesses; disagreement yields `UNDEFINED_WITNESS_VARIANCE`.

Source and observation thresholds are separated as `epsilon_src` and `epsilon_obs`, linked by `ThresholdMap_x`. A shared threshold requires a separate shared-scale proof.

The evaluator returns `COMPATIBLE`, `INCOMPATIBLE`, or `UNDEFINED`, with the propositional `BCon_FCI005Distinction_x` projection permitted only for `COMPATIBLE`.

The expanded six-test bridge suite has not yet been run. `BCon_x` remains unbound and `H_x` remains undeclared.
