# Proof P034 - MT-001 Restricted Local Proof (Projection Idempotence Under Stable Admissibility)

## 0. Metadata
- **proof_id**: P034
- **theorem_id**: MT-001
- **status**: restricted_local_argument_only
- **proof_type**: conditional_local_idempotence
- **rigor_level**: TS3_LOCAL_ARGUMENT
- **compliance**: [Compliance Charter v2.3](../../../../../../registry/compliance_charter_v2_3.json)

## 1. Goal
Provide an additive restricted-domain proof artifact for the MT-001 statement:

`Pi_A(Pi_A(x)) ~ Pi_A(x)`

under the already declared stable admissibility conditions `SA-001` through `SA-005`.

This artifact does **not** promote MT-001 to a proven theorem. It packages the scaffolded local idempotence argument into an explicit bounded proof attempt and preserves the formal-procedural-only claim scope.

## 2. Uses
- **Scaffold**: `registry/math/pi_a_idempotence_proof_scaffold.json`
- **Quantifier binding**: `registry/math/theorem_quantifier_registry.json` entry `TQ-001`
- **Equivalence property binding**: `registry/math/equivalence_property_registry.json` entry `EQP-001`
- **Equivalence relation binding**: `registry/math/equivalence_relation_registry.json` relation `projection_equivalence`
- **Boundary binding**: `registry/math/theorem_boundary_condition_registry.json` entry for `MT-001`
- **Root floor**: `(E != 0) iff_R delta_a(E > 0)`

## 3. Scope and Non-Claims
- **Scope**: formal procedural only
- **Domain**: bounded process states in the declared `Pi_A` domain `D_A` under stable admissibility
- **Does not claim**:
  - global idempotence
  - idempotence under dynamic admissibility windows
  - idempotence under residue drift
  - idempotence under orientation conflict
  - physical truth
  - theorem promotion above restricted local argument status

## 4. Assumptions
Let:
- `x` be a candidate process state in the declared domain `D_A`.
- `y := Pi_A(x)` be the first admissibility projection.
- `z := Pi_A(y)` be the second admissibility projection.
- `~` denote the restricted `admissibility_equivalence` relation.

Assume:
- **SA-001**: the admissibility window `A` is non-empty.
- **SA-002**: `Pi_A` maps every candidate in its declared domain into `A`.
- **SA-003**: for any `y in A`, `Pi_A(y) ~ y` under the declared admissibility equivalence relation.
- **SA-004**: residue and orientation constraints remain stable between first and second application.
- **SA-005**: no boundary drift changes `A` between `Pi_A(x)` and `Pi_A(Pi_A(x))`.

## 5. Proof
We show that, within the declared stable admissibility domain, the second application of `Pi_A` does not change the admissibility-equivalence class established by the first application.

### Step 1: First projection lands inside the admissibility window
Define `y := Pi_A(x)`.

By `SA-002`, the first application of `Pi_A` maps the candidate into the admissibility window `A`. So:

`y in A`.

This is the decisive entry condition for the second application.

### Step 2: Stable window and stable context preserve the second application domain
By `SA-004`, residue and orientation constraints do not change between the first and second application.
By `SA-005`, no boundary drift changes the admissibility window `A` between the first and second application.

Therefore the second application of `Pi_A` is evaluated in the same admissibility context relevant to the first projected state `y`.

This prevents hidden reclassification by context change during the repeated application.

### Step 3: Fixed-point-style equivalence on states already inside the window
Define `z := Pi_A(y)`.

Since `y in A` from Step 1, `SA-003` applies directly. Therefore:

`z ~ y`.

Substituting the definitions of `y` and `z`, we obtain:

`Pi_A(Pi_A(x)) ~ Pi_A(x)`.

### Step 4: Restricted idempotence conclusion
Inside the bounded domain `D_A` and under the declared stable admissibility conditions, the second projection does not alter the admissibility-equivalence class of the first projection.

So the restricted idempotence statement holds:

`Pi_A(Pi_A(x)) ~ Pi_A(x)`.

## 6. Boundary Case Handling
The theorem boundary registry declares three active cases for `MT-001`.

### 6.1 admissibility_window_collapse
If the admissibility window collapses to empty, then `SA-001` fails and the proof domain no longer applies. This is a scoped failure path, not a contradiction to the restricted theorem statement.

### 6.2 epsilon_null_boundary_flip
If the candidate lies exactly on or crosses the null/non-null threshold so that admissibility classification flips, then the bounded proof requires a symbolic case split not provided here. The theorem is not asserted beyond that boundary.

### 6.3 equivalence_boundary_failure
If `admissibility_equivalence` itself fails because context changed or because the relevant preserved features are no longer shared, then `SA-003` is not available and the idempotence claim is out of scope.

## 7. Root-Trace Reading
This proof stays root-traceable to `(E != 0) iff_R delta_a(E > 0)` in a restricted sense:
- `Pi_A` is a local admissibility-filtering structure on the realized continuation side,
- the first projection establishes a state already inside the admissibility window,
- under stable residue, orientation, and boundary conditions, reapplying the same admissibility filter does not produce a new admissibility-equivalence class.

This artifact does not derive the full operator algebra of `Pi_A` from the root floor. It only packages the local idempotence consequence under the already declared `SA-*` assumptions.

## 8. Conclusion
Within the declared stable admissibility assumptions `SA-001` through `SA-005`, MT-001 has a valid restricted local proof artifact:

`Pi_A(Pi_A(x)) ~ Pi_A(x)`.

This strengthens theorem-facing packaging for local projection idempotence without altering theorem status or removing any named failure boundaries.

## 9. Residual Limits
- This artifact does not prove global idempotence.
- This artifact does not prove idempotence under changing admissibility windows.
- This artifact does not resolve threshold-sensitive null-boundary cases.
- This artifact does not eliminate the need for broader theorem-closure review.

## 10. Status Footer
- **Status**: restricted_local_argument_only
- **Theorem status**: not proven
- **Claim ceiling**: formal_procedural_only
- **Authority**: additive proof artifact for local theorem maintenance only
