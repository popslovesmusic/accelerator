# Ordered `S/s` Orientation Evaluator

## Status

`DEFINITION_CANDIDATE`

- Source packet obligation: `OBL-02`
- Related packet obligation: `OBL-01`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Scope: finite alphabet `A = {S,s}` and first-order ordered pairs only.

## Alphabet typing

`S` and `s` are distinct placeholder orientation tokens. This note does not assign them physical, scalar, or universal ontological meaning. The distinction is syntactic and relational until a domain-specific interpretation is separately typed.

## Evaluator

For `A = {S,s}`, define the bounded evaluator:

```text
Eval_A(*|*) := A × A
```

with ordered output:

```text
{S|S, S|s, s|S, s|s}
```

The evaluator preserves left and right participation positions. Therefore `S|s` and `s|S` are distinct outputs unless a separately declared reorientation relation establishes equivalence.

## Limits

This is a finite syntactic evaluator. It does not define the primitive bar’s full semantics, derive `→_x`, establish closure `Cl_x`, or support QM-GR or physical claims.
