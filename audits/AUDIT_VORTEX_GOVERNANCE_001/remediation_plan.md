# Remediation Plan (AUDIT_VORTEX_GOVERNANCE_001)

## 1. Identified Gaps
- **Harness Registration Gap (V3):** The prototype testing script `tests/test_vortex_admissibility.py` needs to be registered as an experimental validation harness.
- **Backend Discrepancy (V4):** The campaign configuration declared `triadic_closure_substrate_sim_cpp` as the target execution engine, but a Python prototype was run.
- **Metric Definition Gap (V4):** The mathematical formulation for `organization_score` needs to be formally added to `registry/math/metric_registry.json`.

## 2. Action Items
1. **Register the Python Prototype Harness**: Add `tests/test_vortex_admissibility.py` to `registry/tool_index.json` under an experimental/prototype status.
2. **Formally Register the Metrics**: Add `organization_score` and `delta_alpha` definitions to `registry/math/metric_registry.json`.
3. **Execute C++ Equivalence Run**: Write a bridge script to execute the vortex sweep using the native C++ engine (`triadic_sim.exe` via `sim_governed.py`) to confirm that the C++ substrate exhibits the same self-conditioning divergence signatures as observed in the Python prototype.
4. **Remove Governance Hold**: Once the C++ runs are validated and metrics are synced, transition `H1_vortex_admissibility` from `EVIDENCE_UNDER_GOVERNANCE_AUDIT` back to `C2_test_designed` with `CAMPAIGN_EVIDENCE_RECORDED` status.
