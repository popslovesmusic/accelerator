# S Arbitration Definition

## Scope

This note records a formal definition candidate for the `S` stage inside `delta_a`. Scope is limited to pre-arbitration pruning structure. Claim class: `C1 formal definition candidate`. No theorem promotion, topology promotion, geometry promotion, or physics-app promotion follows from this artifact alone.

## Directly observed or defined

**Canonical symbol:** `S`

**Canonical name:** `Sequential Pruning Operator`

**Canonical form:**
```text
S_R,A(C_t) -> C_t^S
```

**Reading:** Given a candidate continuation set `C_t` produced under `delta_a`, `S` removes candidates that fail sequential admissibility constraints before `Arb_A` selects a realized continuation.

**Pipeline position:**
```text
E(chi_D) > 0
delta_a generates candidate continuation set C_t
S_R,A prunes C_t into C_t^S
Arb_A selects q* from C_t^S
Delta realizes q*
```

**Formal candidate:**
```text
C_t := { q_i | q_i is admissible under initial delta_a constraints }
C_t^S := { q_i in C_t | S_R,A(q_i, chi_D, R_<->, A_adm) = PASS }
C_t^S = emptyset -> admissibility branch collapse or re-orientation trigger review
```

**Sequential pruning order:**
1. type admissibility
2. nonzero distinction check
3. residue compatibility
4. topology preservation
5. orientation compatibility

## Inferred inside framework

Inside the present framework draft, `S` is treated as an internal `delta_a` stage that makes the pre-arbitration subset explicit. The result is a cleaner separation between admissibility pruning and realization arbitration: `S` removes inadmissible candidates, while `Arb_A` chooses among the survivors.

## External resemblance

This can be compared, by analogy only, to a constrained preprocessing or gating pass that runs before a decision rule. The analogy is procedural only and does not identify `S` with any external physical, computational, or ontological mechanism.

## What It Does Not Prove

- `S` is not `Arb_A`.
- `S` does not select the realized continuation.
- `S` does not compute `T_class`.
- `S` does not define residue.
- `S` does not justify topology, geometry, or physics-app claims.
- `S` does not by itself promote any theorem, bridge, or empirical claim.

## Failure Modes and Uncertainty

- If `C_t^S = emptyset`, the branch collapses or must be reviewed for re-orientation.
- The exact implementation semantics of each pruning predicate remain validation targets.
- This note defines internal sequencing only; it does not settle uniqueness, completeness, or empirical adequacy of arbitration outcomes.
