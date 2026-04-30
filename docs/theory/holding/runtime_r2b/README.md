# Runtime R2B

`runtime_r2b` is a research-only non-scalar successor to frozen `runtime_r2`.

It is **not** an authority branch. Its job is to test one narrow question:

- if directional coexistence, split eligibility, and scaffold commitment are
  separated into stages, does the `runtime_r2` universal-lock failure relax
  into a more meaningful local window?

## Branch role

`runtime_r2b` keeps the two-channel directional node state:

- `forward`
- `reverse`

Edges still carry relational structure:

- admissibility
- residue
- split eligibility
- tension
- barrier scaffold

The key difference from `runtime_r2` is that scaffold is no longer driven
directly from raw coexistence pressure. The intended stage order is:

1. coexistence recognition
2. split eligibility
3. tension growth
4. barrier scaffold commitment

## Research rules

- research only
- no PDE-facing claims
- no promotion claims by default
- same packaged local-window anchors used for `runtime_r1c`
- document insights after each substantial run

## Immediate frame

Primary anchor set:

- quiet reference near `0.08`
- first precursor `0.10`
- middle precursor `0.14`
- corridor interior `0.20`
- split onset `0.23`
- split center `0.24`
- barrier lock `0.25`

Primary causal ablations:

- full
- eligibility off
- scaffold off

The branch only warrants continuation if stage-gated eligibility creates real
internal separation that frozen `runtime_r2` could not.
