# Proof P032 - MT-003 Restricted Local Proof (Non-Empty Admissible Image)

## 0. Metadata
- **proof_id**: P032
- **theorem_id**: MT-003
- **status**: restricted_local_argument_only
- **proof_type**: conditional_local_implication
- **rigor_level**: TS3_LOCAL_ARGUMENT
- **compliance**: [Compliance Charter v2.3](../../../../../../registry/compliance_charter_v2_3.json)

## 1. Goal
Provide an additive restricted-domain proof artifact for the MT-003 statement:

`existence(continuation_event) => image(Pi_A o delta_selection(candidate_set)) != empty`

This artifact does **not** promote MT-003 to a proven theorem. It packages the already-declared `NEI-001` through `NEI-005` assumptions into an explicit contradiction argument and preserves the bounded claim scope.

## 2. Uses
- **Scaffold**: `registry/math/continuation_nonempty_image_proof_scaffold.json`
- **Quantifier binding**: `registry/math/theorem_quantifier_registry.json` entry `TQ-002`
- **Boundary binding**: `registry/math/theorem_boundary_condition_registry.json` entry for `MT-003`
- **Root floor**: `(E != 0) iff_R delta_a(E > 0)`

## 3. Scope and Non-Claims
- **Scope**: formal procedural only
- **Domain**: bounded continuation candidate set `C` with declared pruning constraints and non-null participation context
- **Does not claim**:
  - global continuation existence
  - uniqueness of continuation
  - physical actualization
  - continuation under empty admissibility window
  - continuation under total residue/orientation rejection
  - theorem promotion above restricted local argument status

## 4. Assumptions
Let:
- `C` be the declared continuation candidate set.
- `delta_selection(C)` be the candidate subset surviving the declared selection and pruning rules.
- `Pi_A` be the admissibility projection/filter.
- `I_A := image(Pi_A o delta_selection)` be the admissible image of the selected candidates.

Assume:
- **NEI-001**: participation space contains at least one non-null locus under the declared epsilon-null rule.
- **NEI-002**: the relevant admissibility window is non-empty.
- **NEI-003**: `Pi_A` maps at least one candidate continuation into the admissibility window.
- **NEI-004**: `delta_selection` leaves at least one admissible candidate after selection and pruning.
- **NEI-005**: residue/orientation constraints do not eliminate all candidate continuations.

## 5. Proof
We prove the contrapositive exclusion required by MT-003 inside the declared bounded domain.

### Step 1: Continuation event membership requirement
By the operational meaning of `continuation_event`, any realized continuation event must arise from the declared candidate continuation pipeline. Therefore if a continuation event exists, there must be some witness candidate `c` drawn from `C` that survives the selection stage and remains admissible after projection.

Formally, if `existence(continuation_event)` holds, then there exists a witness `c` such that:

`c in C`, `delta_selection(c)` is retained, and `Pi_A(delta_selection(c)) in I_A`.

This is exactly the bounded existential reading recorded in `TQ-002`.

### Step 2: Empty admissible image blocks witness existence
Assume for contradiction that `existence(continuation_event)` holds while `I_A = empty`.

If `I_A = empty`, then no selected candidate survives admissibility projection. Hence there is no witness `c` such that `Pi_A(delta_selection(c))` lies in the admissible image. This contradicts Step 1.

Therefore:

`existence(continuation_event) => I_A != empty`.

### Step 3: Relation to NEI-003 and NEI-004
The contradiction is not merely semantic. It is operationally tied to the declared conditions:
- If `NEI-003` fails, admissibility projection contributes no candidate to the image, so `I_A` may be empty and no continuation event is licensed.
- If `NEI-004` fails, total branch pruning removes all selected candidates before admissibility projection, so `I_A` may be empty and no continuation event is licensed.

Thus the theorem statement is conditional on the survival of at least one admissible witness through both the selection and admissibility stages.

### Step 4: Restricted case split for total branch pruning
The active boundary case `total_branch_pruning` requires symbolic case handling. Inside the present restricted domain, the case split is:

1. If total branch pruning occurs, then `delta_selection(C) = empty`.
2. If `delta_selection(C) = empty`, then `I_A = image(Pi_A o delta_selection) = empty`.
3. If `I_A = empty`, Step 2 blocks `existence(continuation_event)`.

So total branch pruning is not a counterexample to MT-003. It is a named failure pathway in which the antecedent cannot be realized inside the declared domain.

### Step 5: Root-trace reading
The proof remains root-traceable to `(E != 0) iff_R delta_a(E > 0)` in the following restricted sense:
- A continuation event is a realized continuation claim on the right-hand side of the root floor.
- The non-empty admissible image is the minimal witness structure required for that realized continuation claim.
- If the admissible image is empty, the right-hand continuation side is not instantiated, so no continuation event may be asserted.

This does not derive every detail of `Pi_A` or `delta_selection` from the root floor. It only shows that empty admissible image is incompatible with the existence of a continuation event under the declared local semantics.

## 6. Conclusion
Within the declared `NEI-*` assumptions and bounded existential scope, MT-003 has a valid restricted local implication proof:

`existence(continuation_event) => image(Pi_A o delta_selection(candidate_set)) != empty`.

This closes the direct contradiction step needed for the theorem-facing statement, while preserving all existing scope limits and non-promotion constraints.

## 7. Residual Limits
- This artifact does not prove global continuation existence.
- This artifact does not prove that admissible witnesses always exist.
- This artifact does not prove that `Pi_A` or `delta_selection` are total operators.
- This artifact does not eliminate the need for broader theorem-closure review or external validation.

## 8. Status Footer
- **Status**: restricted_local_argument_only
- **Theorem status**: not proven
- **Claim ceiling**: formal_procedural_only
- **Authority**: additive proof artifact for local theorem maintenance only
