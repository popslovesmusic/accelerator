-- Governance runtime patch-chain migration.
-- Exposes a runtime-facing patch-chain projection from the decision log.

DROP VIEW IF EXISTS patch_chain_view;

CREATE VIEW patch_chain_view AS
SELECT
    patch_id,
    requested_action,
    decision,
    reason,
    blocking_conditions,
    dependency_resolution,
    provenance_resolution,
    validator_resolution,
    db_snapshot_at,
    created_at,
    'decision_log_projection' AS coverage_state
FROM governance_decision_log;
