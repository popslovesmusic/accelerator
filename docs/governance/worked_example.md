# A|E Slot-Occupancy Worked Example (DOC_WORKED_EXAMPLE_046_REVISION_001)

## 1. Status
Provisional documentation note for the revised worked example in [`worked_example.json`](./worked_example.json).

This note is documentation-only. It does not modify `RT_core`, does not promote `PATCH_PI_RT_CALCULUS_046` to theorem status, and remains theorem-humble while tracking the applied registry candidate.

## 2. Purpose
The worked example records RT nesting as an ordered continuation process:

1. Continuation `C`
2. Normalization `NF(C)`
3. RT closure
4. Explicit domain rebinding into receiving domain `x`
5. Role occupancy as `A-slot` or `E-slot`
6. Candidate nested RT expression

## 3. Source Artifacts
- [`PATCH_PI_RT_CALCULUS_045.json`](../../registry/governance/patches/PATCH_PI_RT_CALCULUS_045.json)
- [`PATCH_PI_RT_CALCULUS_046.json`](../../registry/governance/patches/PATCH_PI_RT_CALCULUS_046.json)
- [`worked_example.json`](./worked_example.json)
- [`worked_example_operational_046.json`](./worked_example_operational_046.json)
- [`admissibility_trace_046.json`](./admissibility_trace_046.json)
- [`swap_test_046.json`](./swap_test_046.json)
- [`mono_process_textbook_complete.md`](../textbook/mono_process_textbook_complete.md)

## 4. Canonical Pipeline
The note treats the following as the relevant ordering for a candidate witness:

- Continuation
- Normalization
- RT closure
- Domain rebinding
- Slot occupancy
- Candidate nested RT formation

The ordering matters. Closure precedes rebinding, and rebinding precedes occupancy.

## 5. Worked Witness

### 5.1 Premises
- `C_A` denotes a candidate continuation intended for possible A-slot occupancy.
- `C_E` denotes a candidate continuation intended for possible E-slot occupancy.
- `NF(C_A)` yields `CompletedRT_A` only if `C_A` closes under the governing RT condition.
- `NF(C_E)` yields `CompletedRT_E` only if `C_E` closes under the governing RT condition.
- `x` declares the shared receiving nesting domain.
- `S` denotes the shared substrate/scale of the receiving A|E window.
- `r` records residue or history for the enclosing window.

### 5.2 Ordered Construction

**A path**

`C_A -> NF(C_A) -> CompletedRT_A := RT(NF(C_A)) -> Rebind_x(CompletedRT_A) -> A_x(CompletedRT_A)`

**E path**

`C_E -> NF(C_E) -> CompletedRT_E := RT(NF(C_E)) -> Rebind_x(CompletedRT_E) -> E_x(CompletedRT_E)`

**Candidate nesting**

`<A_x(CompletedRT_A) | E_x(CompletedRT_E)>_r`

### 5.3 Admissibility Rule
`AE_SLOT_OCCUPANCY_WITNESS_RULE_001`:

A completed RT may appear in an A-slot or E-slot only after it is explicitly rebound into the receiving domain `x` and typed according to the slot it occupies.

The forbidden inference is explicit: `RT(X)` alone does not imply automatic admissibility into `A` or `E`.

### 5.4 Swap Test

`<A_x(CompletedRT_E) | E_x(CompletedRT_A)>_r`

The swapped construction must be checked independently. If admissibility changes under swap, A/E occupancy is role-asymmetric or domain-dependent.

## 6. Audit Reading
This witness supports the following bounded readings only:

- Candidate slot occupancy is available only under explicit rebinding.
- RT closure precedes slot occupancy.
- The example does not prove A-slot/E-slot symmetry.
- The example does not prove universal nesting.
- `R` as relation and `r` as residue or history remain distinct.

## 7. Claim Humility
This note is a candidate witness only.

It does not:

- assert A-slot/E-slot symmetry
- assert universal RT occupancy
- assert theorem status
- identify `OPEN_BRIDGE_001` closure with basin closure
- promote `<*>_x` from meta-language construct to proof operator

## 8. Revision Boundary
This revision is intentionally narrow. It documents the ordering and typing of a candidate nested RT witness, but it does not complete the open follow-up checks in `PATCH_PI_RT_CALCULUS_046`.

---
[Back to Governance Index](../README.md)
