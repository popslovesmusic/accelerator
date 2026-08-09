# Routing And Candidate Flow

## Before
- Surface wording reached request handling before a canonical governed identity was frozen.
- `request_id` participated in the governed capsule hash, so equivalent `task` and `query` requests could diverge.
- Retrieval variants such as `foo`, ` foo `, and `FOO` did not share a stable bounded candidate identity.

## After
- Surface requests normalize into `canonical_routed_request_v1` before cache lookup.
- `orientation_retrieval` and `memory_retrieval` both route to `artifact_retrieval`.
- Candidate sets are built from a finite governed universe, deduplicated, ordered deterministically, and hashed before cache lookup.
- Zero-candidate, single-candidate, and strictly dominant candidate cases resolve deterministically.
- Unknown operations return `ROUTE_UNRESOLVED` instead of creating an ad hoc path.

## Observed Effects
- Equivalent retrieval variants now share one candidate-set hash.
- Task/query governed capsules now converge on the same capsule hash once incidental request metadata is excluded.
- Repository scans found no independent router or open-universe candidate path in the governed surfaces exercised by the patch.
