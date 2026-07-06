-- Governance runtime current-state migration.
-- Replaces the bootstrap placeholder current-state view with a state-aware projection.

DROP VIEW IF EXISTS current_state_view;

CREATE VIEW current_state_view AS
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
    (SELECT COUNT(*) FROM artifacts WHERE orientation_status = 'invalidated') AS invalidated_count,
    (SELECT COUNT(*) FROM governance_decision_log) AS decision_count,
    (SELECT decision_id FROM governance_decision_log ORDER BY COALESCE(created_at, db_snapshot_at) DESC, id DESC LIMIT 1) AS latest_decision_id,
    (SELECT patch_id FROM governance_decision_log ORDER BY COALESCE(created_at, db_snapshot_at) DESC, id DESC LIMIT 1) AS latest_decision_patch_id,
    (SELECT decision FROM governance_decision_log ORDER BY COALESCE(created_at, db_snapshot_at) DESC, id DESC LIMIT 1) AS latest_decision_decision,
    (SELECT reason FROM governance_decision_log ORDER BY COALESCE(created_at, db_snapshot_at) DESC, id DESC LIMIT 1) AS latest_decision_reason,
    (SELECT created_at FROM governance_decision_log ORDER BY COALESCE(created_at, db_snapshot_at) DESC, id DESC LIMIT 1) AS latest_decision_at,
    'RT := [(ℰ≠0) ⇔R δα(ℰ>0)]' AS current_rt,
    CASE
        WHEN (
            SELECT COUNT(*)
            FROM semantic_authority_view
            WHERE semantic_key IN ('RT_CORE', 'META_A_BINDING', 'META_B_BINDING')
              AND status = 'active'
        ) = 3 THEN 'semantic_projection_ready'
        ELSE 'semantic_projection_partial'
    END AS semantic_projection_state,
    (SELECT COUNT(*) FROM semantic_authority_view) AS semantic_authority_count,
    CASE
        WHEN (SELECT COUNT(*) FROM semantic_authority_view) > 0 THEN 'projected'
        ELSE 'empty'
    END AS semantic_authority_graph_state,
    (SELECT COUNT(*) FROM claim_evidence_links) AS claim_evidence_link_count,
    (SELECT COUNT(DISTINCT claim_id) FROM claim_evidence_links) AS claim_evidence_claim_count,
    CASE
        WHEN (SELECT COUNT(*) FROM claim_evidence_links) > 0 THEN 'projected'
        ELSE 'empty'
    END AS claim_evidence_state,
    CASE
        WHEN (SELECT COUNT(*) FROM artifacts WHERE orientation_status IN (
            'historical_residue',
            'archived',
            'superseded',
            'invalidated',
            'unverified_residue'
        )) > 0 THEN 'historical_residue_compressed'
        ELSE 'historical_residue_clear'
    END AS historical_residue_state,
    'active' AS db_first_gate_state,
    'registry' AS active_authority,
    'mixed' AS authority_boundary,
    NULL AS open_runtime_debt_count,
    NULL AS live_blocker_count,
    CASE
        WHEN (SELECT MAX(indexed_at) FROM artifacts) IS NULL THEN 'unknown'
        WHEN julianday('now') - julianday((SELECT MAX(indexed_at) FROM artifacts)) > 14 THEN 'stale_snapshot_warning'
        ELSE 'current'
    END AS snapshot_freshness,
    CASE
        WHEN (SELECT COUNT(*) FROM governance_decision_log) > 0 THEN 'stateful_projection'
        ELSE 'bootstrap_projection'
    END AS coverage_state;
