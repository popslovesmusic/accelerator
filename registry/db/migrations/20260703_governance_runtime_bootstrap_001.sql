-- Governance runtime bootstrap migration.
-- Adds decision logging and bootstrap views for DB-first governance gating.

CREATE TABLE IF NOT EXISTS governance_decision_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id TEXT UNIQUE NOT NULL,
    patch_id TEXT NOT NULL,
    campaign_id TEXT,
    requested_action TEXT,
    decision TEXT NOT NULL,
    reason TEXT NOT NULL,
    blocking_conditions TEXT,
    authority_resolution TEXT,
    dependency_resolution TEXT,
    provenance_resolution TEXT,
    validator_resolution TEXT,
    db_snapshot_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operator TEXT,
    evidence_json TEXT,
    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_governance_decision_log_patch_id
    ON governance_decision_log(patch_id);

CREATE INDEX IF NOT EXISTS idx_governance_decision_log_campaign_id
    ON governance_decision_log(campaign_id);

CREATE INDEX IF NOT EXISTS idx_governance_decision_log_created_at
    ON governance_decision_log(created_at);

CREATE VIEW IF NOT EXISTS governance_runtime_decision_view AS
SELECT
    decision_id,
    patch_id,
    campaign_id,
    requested_action,
    decision,
    reason,
    blocking_conditions,
    authority_resolution,
    dependency_resolution,
    provenance_resolution,
    validator_resolution,
    db_snapshot_at,
    created_at
FROM governance_decision_log;

CREATE VIEW IF NOT EXISTS patch_application_gate_view AS
SELECT
    decision_id,
    patch_id,
    campaign_id,
    requested_action AS action,
    decision,
    reason,
    blocking_conditions,
    created_at
FROM governance_decision_log;

CREATE VIEW IF NOT EXISTS authority_resolution_view AS
SELECT
    'registry' AS winning_authority,
    'registry_wins_over_db_on_conflicts' AS policy_id,
    'Registry remains authoritative; DB runtime is an operational gate only.' AS rule_text,
    'bootstrap' AS coverage_state;

CREATE VIEW IF NOT EXISTS current_state_view AS
SELECT
    (SELECT MAX(indexed_at) FROM artifacts) AS latest_artifact_indexed_at,
    (SELECT COUNT(*) FROM artifacts) AS artifact_count,
    (SELECT COUNT(*) FROM artifacts WHERE orientation_status = 'canonical_active') AS canonical_active_count,
    (SELECT COUNT(*) FROM artifacts WHERE orientation_status = 'active_runtime') AS active_runtime_count,
    (SELECT COUNT(*) FROM artifacts WHERE orientation_status IN (
        'historical_residue',
        'archived',
        'superseded',
        'invalidated',
        'unverified_residue'
    )) AS residue_count,
    'registry' AS active_authority,
    NULL AS current_rt,
    NULL AS open_debt_count,
    NULL AS live_blocker_count,
    'partial_bootstrap' AS coverage_state;
