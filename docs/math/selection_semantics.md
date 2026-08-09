# Selection Semantics Registry (MPF-FSUB-007)

## 1. Purpose
Clarify whether $\delta$ is treated as a relation, set-valued map, partial function, or selected update rule under restricted conditions.

## 2. Semantic Classes
### 2.1 DELTA_RELATIONAL
- **Class ID**: `DELTA_RELATIONAL`
- **Definition**: $\delta$ is treated as a general relation between process states and continuation events.

### 2.2 DELTA_SET_VALUED
- **Class ID**: `DELTA_SET_VALUED`
- **Definition**: $\delta$ is a map from states to sets of admissible continuation candidates.

### 2.3 DELTA_PARTIAL_FUNCTION_UNDER_RULE
- **Class ID**: `DELTA_PARTIAL_FUNCTION_UNDER_RULE`
- **Definition**: $\delta$ behaves as a partial function when a specific selection rule is applied.

### 2.4 DELTA_SINGLE_VALUED_WITH_TIE_BREAK
- **Class ID**: `DELTA_SINGLE_VALUED_WITH_TIE_BREAK`
- **Definition**: $\delta$ always returns a single actualization via a mandatory tie-breaking policy.

### 2.5 DELTA_UNDEFINED_ON_FAILURE
- **Class ID**: `DELTA_UNDEFINED_ON_FAILURE`
- **Definition**: $\delta$ is formally undefined if the admissible image $Im_A$ is empty.

## 3. Required Policies
- **degeneracy_handling**: Rule for managing multiple equivalent admissible images.
- **tie_breaking_policy**: Formal mechanism for selecting a single continuation.
- **empty_image_policy**: Governance for CASE(orientation locking).
- **branch_explosion_policy**: Limits on divergent pathways.
- **failure_preservation_policy**: Requirement to record selection failures.

## 4. Governance Status
- **Theorem Status**: NOT_PROVEN
- **Series Status**: FORMAL_SUBSTRATE_SCAFFOLD
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

## 5. Governance Rules
- **SS-RULE-001**: $\delta$ must specify its active semantic class and associated policies.
- **SS-RULE-002**: Selection semantics remain strictly local to the declared CSI neighborhood.

## 6. Forbidden Claims
- Selection semantics prove physical choice or free will.
- Tie-breaking policies derive physical selection constants.
- Divergent selection justifies the assumption of absolute parallel universes.

## 7. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](codex_master_index.md)
