# Known Limits

- Determinism: the engine initialization is fixed (no RNG/noise path); seed-based uncertainty is not applicable unless the engine is extended.
- Config schema: the C++ engine reads a *flat* JSON schema (e.g., `nx`, `steps`, `dt`, `kappa`, `lambda_R`, `s`). Nested `grid/model` configs are ignored by the engine.
- Hardware: GPU path uses default SYCL selector; device choice may vary by host configuration.
