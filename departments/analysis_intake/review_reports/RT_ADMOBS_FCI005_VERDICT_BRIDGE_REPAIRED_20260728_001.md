# Repaired FCI-005 Verdict and Bridge Support

The effective threshold relation is now explicit and typed through `ThresholdMapResult_x`. Shared-scale handling is centralized in `EvalEffectiveThresholdRelation_x`.

`PermittedFCI005BridgeWitness_x` now requires immutable source identifiers, carrier and context provenance, ordered-pair applicability, and pre-`RefOrient_x` / pre-`ProjectBounded` evaluation. The structural witness no longer fixes the threshold result.

`EvalInvariantBridgeVerdict_x` exposes the common final pair verdict as `PAIR_PASS`, `PAIR_FAIL`, or `UNDEFINED`. Pair direction is ordered by default. Empty or undeclared applicable evaluator sets cannot pass by vacuous quantification.

The evaluator subsuite remains definition-level passing. Tests requiring actual source witnesses, context mapping, threshold provenance, and dependency closure remain open and are not claimed as passed.
