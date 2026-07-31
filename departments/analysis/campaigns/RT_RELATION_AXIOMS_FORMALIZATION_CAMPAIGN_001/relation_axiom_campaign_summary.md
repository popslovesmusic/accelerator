# Relation Axiom Formalization Campaign

## Status

AX-R01 and AX-R02 are formalized provisionally. AX-R03 is `INAPPLICABLE` for `|`; whole-RT identity is separate. Typed operand-distinction semantics are provisionally formalized. The authorized `NO_NONTRIVIAL_EQUIVALENCE` path resolves AX-R04 to trivial reference identity only. AX-R05 is `INAPPLICABLE` because the codomain is not an operand domain, and AX-R06 is `RESOLVED_NOT_CLOSED` for the same typed-codomain reason. Whole-RT composition, whole-RT closure, and operand projection remain separate open obligations.

## Observed and created

- Twelve independently addressable proof-obligation records were created.
- A typed dependency graph connects `SymmetryConditionRelation` to each obligation.
- Downstream projection and executable-semantics dependencies are recorded as blocked where applicable.
- Cycle, typing, schema, and read-only checks passed for these campaign artifacts.
- AX-R01 defines only directional typing; it does not establish commutativity, substitution, or composition.
- AX-R02 rejects generic `SymmetryCondition` coercion and same-type operand pairs; it does not add substitution or composition.
- AX-R03 introduces no identity element and does not infer a monoid, group, semigroup, or closed operation.
- AX-R04 permits only reference identity and governed alias normalization; general substitution remains blocked.
- No equivalence relation, substitution permission, or congruence permission was created.
- The formalization records required properties and failure conditions only; it does not define `≈_B`, `≈_U`, or `≈_SC`.
- Whole-RT identity remains a separate open obligation.
- No self-composition, closure law, or implicit projection was introduced.
- AX-R06 does not establish operator invalidity or whole-RT nonclosure; it records only operator-local nonclosure.
- `Dist_B`, `Dist_U`, and `Dist_SC` require typed witnesses; absence of a witness does not establish equivalence.

## Not established

No axiom was proved, rejected, or promoted. Existing mathematical definitions, primitive semantics, proofs, and executable semantics were not changed. The result does not establish canonical mathematical correctness or physical correspondence.

## Remaining open work

AX-R01 through AX-R12 remain OPEN. Each requires its own governed treatment, evidence, and proof disposition before any downstream blocker can be considered resolved.

Claim ceiling: `C1_MODEL_RELATIVE`.
