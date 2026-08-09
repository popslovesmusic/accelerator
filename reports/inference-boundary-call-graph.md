# Inference Boundary Call Graph

## Boundary Source

- [tools/signal_scope_phase_continuation_engine/core/semantic_readout.py](/D:/projects/acellorator/tools/signal_scope_phase_continuation_engine/core/semantic_readout.py):1105-1271 contains the optional network boundary.
- [tools/inference_governance/inference_necessity_gate.py](/D:/projects/acellorator/tools/inference_governance/inference_necessity_gate.py):478-636 contains the shared necessity gate.
- [registry/inference_boundary_registry.json](/D:/projects/acellorator/registry/inference_boundary_registry.json) registers the semantic readout boundary as LATENT.

## Call Flow

- `generate_structured_reply`
  - [tools/signal_scope_phase_continuation_engine/core/semantic_readout.py](/D:/projects/acellorator/tools/signal_scope_phase_continuation_engine/core/semantic_readout.py):1321-1386
  - Dispatches to `_openai_compatible_reply` for the network backend and `_local_readout_result` for deterministic fallback.

- `_openai_compatible_reply`
  - [tools/signal_scope_phase_continuation_engine/core/semantic_readout.py](/D:/projects/acellorator/tools/signal_scope_phase_continuation_engine/core/semantic_readout.py):1105-1271
  - Builds the request payload, checks subordinate boundary conditions, and calls the shared necessity gate.
  - When the shared gate authorizes, it performs exactly one `urllib.request.urlopen` call.
  - When the gate denies or the request fails, it returns the local deterministic reply.

- `_semantic_readout_capability_gate`
  - [tools/signal_scope_phase_continuation_engine/core/semantic_readout.py](/D:/projects/acellorator/tools/signal_scope_phase_continuation_engine/core/semantic_readout.py):582-717
  - Builds deterministic attempt and uncertainty records and delegates the inference necessity decision to the shared gate.

- `evaluate_inference_necessity_gate`
  - [tools/inference_governance/inference_necessity_gate.py](/D:/projects/acellorator/tools/inference_governance/inference_necessity_gate.py):478-636
  - Validates the governed capsule, loads the boundary registry, checks deterministic attempts, material uncertainty, candidate bounding, and explicit budget.
  - Emits shared gate telemetry for evaluation and final decision.

## Registered Boundary

- `SEMANTIC_READOUT_OPTIONAL_OPENAI_001`
  - path: `tools/signal_scope_phase_continuation_engine/core/semantic_readout.py`
  - symbol: `_openai_compatible_reply`
  - status: `LATENT`
  - authority class: `PRESENTATION_ONLY`
  - allowed caller: `analysis_intake.worker`
  - allowed purposes: `HUMAN_READABLE_SUMMARY`, `AMBIGUITY_EXPLANATION`, `OPTIONAL_SEMANTIC_COMMENTARY`
  - allowed mode: `CONSTRAINED`
  - retry policy: `default_retry_budget = 0`, `automatic_retry = false`
  - fallback: `_local_reply`

## Negative Surfaces

- Test-only boundary usage remains confined to [tests/test_semantic_readout_capability_gate.py](/D:/projects/acellorator/tests/test_semantic_readout_capability_gate.py):128-128.
- Latent activation configuration remains confined to [tools/signal_scope_phase_continuation_engine/config/config_v14_terminal.json](/D:/projects/acellorator/tools/signal_scope_phase_continuation_engine/config/config_v14_terminal.json):119-119.
- False positive bridge stub remains confined to [gpt_folder_bridge/bridge.py](/D:/projects/acellorator/gpt_folder_bridge/bridge.py):5-11.

## Validation Evidence

- `python -m unittest tests.test_semantic_readout_capability_gate` passed.
- `python -m unittest tests.inference_governance.test_no_ungated_inference_boundaries` passed.
- `python -m py_compile` passed for the changed Python files.

