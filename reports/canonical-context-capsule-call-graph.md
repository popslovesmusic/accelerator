# Canonical Context Capsule Call Graph

## Canonical Producer
- `scripts/query_governance.py:3164` defines `build_governed_context_capsule_v1`.
- `scripts/query_governance.py:3562` exposes `build_governed_context_capsule` as a compatibility alias to the canonical producer.
- `scripts/query_governance.py:6434` projects the canonical capsule into the legacy `build_context_capsule_result` summary path.

## Compatibility Surfaces
- `scripts/agent_memory/memory_retrieval.py:15` calls `build_governed_context_capsule_v1` directly.
- `scripts/agent_memory/memory_packet_builder.py:15` calls `build_governed_context_capsule_v1` directly.
- `scripts/gemini_claim_context.py:15` calls `build_governed_context_capsule_v1` directly.
- `scripts/gemini_trace_context.py:15` calls `build_governed_context_capsule_v1` directly.
- `scripts/gemini_memory_context.py:15` calls `build_governed_context_capsule_v1` directly.
- `scripts/gemini_execution_context.py:15` calls `build_governed_context_capsule_v1` directly.

## Post-Fix Observations
- No listed wrapper performs independent state reconstruction.
- The canonical capsule hash is stable across identical governed inputs.
- The repo-backed cache returns `HIT` on the second identical invocation.

## Tests and Evidence
- `tests/test_governed_context_capsule_v1.py:17` validates the schema artifact.
- `tests/test_governed_context_capsule_v1.py:44` validates the alias and capsule contract.
- `tests/test_governed_context_capsule_v1.py:74` validates cache corruption rejection.
- `tests/test_governed_context_capsule_v1.py:107` validates cache hits on repeated identical inputs.
