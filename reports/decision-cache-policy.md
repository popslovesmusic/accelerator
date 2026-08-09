# 1. Scope
This policy defines the governed decision cache for PATCH_ACCELERATOR_DETERMINISTIC_DECISION_CACHE_053. It covers deterministic decision reuse, accepted constrained output reuse, and negative-cache handling for the semantic readout path and the shared inference necessity gate.

The repository-local store is `state/inference_governance/decision_cache.sqlite3`.

# 2. Directly Observed / Defined
- Class A deterministic results are reusable when they are produced without inference and pass schema validation.
- Class B accepted constrained outputs are reusable only after constrained inference, deterministic validation, and exact dependency match on read.
- Class C rejected or failed outputs may be cached only as negative results when the failure is stable and the invalidation dependencies are complete.
- Class D content is forbidden from reuse.
- Cache keys are derived from canonical request semantics plus governed state, authority, freshness, boundary policy, candidate set, validator version, and output schema version.
- Valid cache hits deny inference before uncertainty and budget authorization.
- Cache miss does not authorize inference.

# 3. Inferred Inside Framework
- Equivalent governed state, equivalent request semantics, equivalent authority, and equivalent candidate bounds should reuse a prior validated result before any inference request is considered.
- A local deterministic semantic reply is a cacheable decision artifact when it depends only on the bounded capsule projection and runtime summary.
- An accepted network reply is a cacheable artifact only when the constrained boundary, schema, validator, and candidate set are unchanged and the result hash revalidates on read.
- A cached advisory output remains advisory; reuse does not elevate it into execution authority.

# 4. External Resemblance
This behaves like a content-addressed memoization layer with explicit invalidation metadata. The resemblance is operational only.

# 5. What It Does Not Prove
- It does not prove semantic similarity matching.
- It does not prove approximate prompt reuse.
- It does not prove cross-project cache portability.
- It does not prove that raw model prose is safe to store or reuse.
- It does not prove that a cache miss justifies inference.

# 6. Failure Modes / Uncertainty
- Any change to capsule hash, authority hash, freshness hash, boundary policy version, deterministic method version, validator version, output schema version, or candidate set invalidates reuse.
- Corrupt rows are treated as misses and invalidated.
- Secret-bearing payloads, raw prompts, and unvalidated free-form model output are non-cacheable.
- If persistence cannot be kept isolated and schema-validated, the safe fallback is in-memory reuse only.
