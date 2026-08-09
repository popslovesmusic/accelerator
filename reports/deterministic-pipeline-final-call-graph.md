# Deterministic Pipeline Final Call Graph

## Canonical Context

- `scripts/query_governance.py:3164` defines `build_governed_context_capsule_v1`.
- `scripts/query_governance.py:3562` exposes a compatibility alias for the canonical producer.
- `scripts/agent_memory/memory_retrieval.py:15`, `scripts/agent_memory/memory_packet_builder.py:15`, `scripts/gemini_claim_context.py:15`, `scripts/gemini_trace_context.py:15`, `scripts/gemini_memory_context.py:15`, and `scripts/gemini_execution_context.py:15` call the canonical producer rather than rebuilding state independently.

## Routing

- `scripts/orientation_retrieval.py` and `scripts/gemini_memory_context.py` converge on the registered governed operation model rather than free-form dispatch.
- `tools/inference_governance/deterministic_router.py` resolves registered operations with no model calls.
- Unknown operations return `ROUTE_UNRESOLVED`.

## Candidate Bounding

- `tools/inference_governance/candidate_policy.py` and `tools/inference_governance/candidate_builder.py` produce finite governed candidate universes.
- Candidate sets are deduplicated, ordered deterministically, and hashed before cache lookup.
- Zero-candidate, single-candidate, and strictly dominant candidate cases resolve without inference.

## Cache And Gate

- `tools/inference_governance/decision_cache.py` stores deterministic results and accepted constrained outputs only.
- `tools/inference_governance/inference_necessity_gate.py` is evaluated after context, caller, purpose, authority, routing, and candidate bounding are frozen.
- A valid cache hit returns `DENY_CACHE_RESULT_AVAILABLE` and bypasses inference.

## Semantic Readout

- `tools/signal_scope_phase_continuation_engine/core/semantic_readout.py` retains one registered latent boundary: `_openai_compatible_reply`.
- The latent boundary has a zero-call default budget, zero retry budget, and a deterministic local fallback.
- The shipped default behavior stays local and deterministic.

## Measured Outcomes

- Canonical context hash stability: identical governed inputs now reuse the same capsule hash.
- Routing convergence: equivalent request wording collapses to one normalized operation and one candidate policy.
- Cache convergence: repeated equivalent deterministic and accepted-output probes reuse prior validated results.
- Default runtime: zero inference calls, zero network requests, zero retries.

## Remaining Debt

- The repository still carries one registered latent boundary for optional semantic commentary.
- That boundary is gated and presentation-only, but it remains a retained inference sink rather than a removed one.
