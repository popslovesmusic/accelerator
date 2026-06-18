# Campaign Design: GEO_PROJECTION_VALIDATION_001

## 0. Metadata
- **Campaign ID**: GEO_PROJECTION_VALIDATION_001
- **Target Operator**: `Pi_geo : Topology_app -> Geometry_app`
- **Target Hardening Note**: `L100`
- **Required Lemma Alias**: `GEO_LEMMA_001`
- **Status**: DESIGNED
- **Minimum Seed Count**: 64
- **Intent**: Evaluate whether candidate topology-to-geometry projections preserve governed invariants strongly enough to remain admissible for provisional downstream use.

## 1. Goal Statement
This campaign evaluates projection legality rather than physical realism. Success is defined as retaining governed invariants during projection with recoverable evidence and explicit loss accounting.

## 2. Governing Question
Given an admissible topology input `T`, does a candidate `Pi_geo` preserve:
- distinction class,
- admissibility status,
- orientation traceability,
- closure traceability?

If not, the projection remains blocked from promotion.

## 3. Control Suite
- `orientation_shuffled`
- `residue_depleted`
- `closure_preserved`
- `closure_perturbed`

These controls are intended to separate genuine invariant retention from artifact, leakage, or trivial smoothing.

## 4. Measurements
- `distinction_loss_rate`
- `orientation_loss_rate`
- `closure_loss_rate`
- `admissibility_violation_rate`

## 5. Acceptance Criteria
- **Distinction Preservation**: No statistically significant distinction collapse relative to control.
- **Orientation Preservation**: Orientation class remains recoverable above the predefined confidence threshold.
- **Closure Preservation**: Closure identity remains traceable after projection.
- **Admissibility Preservation**: No illegal geometry is generated from admissible topology inputs.

## 6. Failure Conditions
- Distinct topology classes collapse into indistinguishable projected geometry.
- Orientation selectors become unrecoverable.
- Closure is destroyed without a separately governed explanatory operator.
- The projection creates geometry outside the admissible legality corridor.

## 7. Critical Path Context
- `aRT_closure_preservation`
- `O_calculus_partial_composition`
- `otimes_non_identity_firewall`
- `OPEN_BRIDGE_001`
- `GEO_LEMMA_001`
- `GEO_PROJECTION_VALIDATION_001`
- `Topology_to_Geometry_Hardening`
- `Field_app`
- `Matter_app`

## 8. Governance Note
This campaign hardens the `Topology_app -> Geometry_app` projection as a legality problem. Passing this campaign would support only governed projection retention claims within scope; it would not, by itself, authorize physical interpretation or universal geometric claims.
