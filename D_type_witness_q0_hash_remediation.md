# Q0 Governance Artifact Hash Remediation

The five Q0 governance inventory artifacts were present on disk and Git-tracked, but their SHA-256 values were absent from `registry/governance_hash_registry.json`. The Q0 runtime therefore reported them as missing during source verification.

Remediation applied:

- registered `governance_ambiguity_register.json`;
- registered `governance_ambiguity_risk_classification.json`;
- registered `governance_authority_relationships.json`;
- registered `governance_remediation_queue.json`;
- registered `governance_surface_inventory.json`.

Verification:

- direct `verify_q0_source_artifacts` check: PASS, five of five verified;
- governance runtime query: executes successfully without missing-artifact errors;
- `scripts/global_validate.py`: completed successfully;
- textbook freshness stage: PASS.

The runtime may still return `defer` for targets outside the governed Q0 authority surface. That is routing behavior, not an artifact-integrity failure.
