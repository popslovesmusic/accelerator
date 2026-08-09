-- Governance runtime context-capsule migration.
-- Builds a compact agent-facing projection from live runtime views.

DROP VIEW IF EXISTS context_capsule_view;

CREATE VIEW context_capsule_view AS
WITH
current_state AS (
    SELECT
        db_first_gate_state,
        authority_boundary,
        latest_decision_id,
        latest_decision_patch_id,
        latest_decision_decision,
        latest_decision_reason,
        coverage_state
    FROM current_state_view
    LIMIT 1
),
authority_state AS (
    SELECT
        authority_owner,
        authority_source,
        conflict_state,
        decision,
        reason,
        warnings
    FROM authority_resolution_view
    ORDER BY
        CASE conflict_state
            WHEN 'mixed' THEN 0
            WHEN 'stale' THEN 1
            WHEN 'unavailable' THEN 2
            ELSE 3
        END,
        target_pattern
    LIMIT 1
),
patch_state AS (
    SELECT
        patch_id,
        status,
        decision,
        reason,
        blocking_conditions
    FROM patch_chain_view
    ORDER BY COALESCE(created_at, db_snapshot_at) DESC
    LIMIT 1
),
replay_state AS (
    SELECT
        COUNT(*) AS replay_subject_count,
        COALESCE(SUM(event_count), 0) AS replay_event_count,
        CASE
            WHEN COUNT(*) > 0 THEN 'projected'
            ELSE 'empty'
        END AS replay_reconciliation_state,
        CASE
            WHEN COUNT(*) > 0 THEN 'diagnostic_only'
            ELSE 'unavailable'
        END AS replay_boundary_state,
        (SELECT subject_id FROM governance_replay_reconciliation_view ORDER BY latest_created_at DESC, subject_id DESC LIMIT 1) AS replay_latest_subject_id,
        (SELECT subject_type FROM governance_replay_reconciliation_view ORDER BY latest_created_at DESC, subject_id DESC LIMIT 1) AS replay_latest_subject_type,
        (SELECT latest_event_id FROM governance_replay_reconciliation_view ORDER BY latest_created_at DESC, subject_id DESC LIMIT 1) AS replay_latest_event_id,
        (SELECT latest_event_type FROM governance_replay_reconciliation_view ORDER BY latest_created_at DESC, subject_id DESC LIMIT 1) AS replay_latest_event_type,
        (SELECT latest_source_patch_id FROM governance_replay_reconciliation_view ORDER BY latest_created_at DESC, subject_id DESC LIMIT 1) AS replay_latest_source_patch_id,
        (SELECT latest_source_path FROM governance_replay_reconciliation_view ORDER BY latest_created_at DESC, subject_id DESC LIMIT 1) AS replay_latest_source_path,
        (SELECT latest_created_at FROM governance_replay_reconciliation_view ORDER BY latest_created_at DESC, subject_id DESC LIMIT 1) AS replay_latest_created_at
    FROM governance_replay_reconciliation_view
),
debt_state AS (
    SELECT
        COUNT(*) AS debt_count,
        SUM(CASE WHEN status IN ('open', 'partial') THEN 1 ELSE 0 END) AS open_or_partial_count,
        SUM(CASE WHEN decision_effect = 'block' THEN 1 ELSE 0 END) AS blocking_count,
        GROUP_CONCAT(debt_id, ',') AS debt_ids
    FROM debt_runtime_view
)
SELECT
    COALESCE((SELECT db_first_gate_state FROM current_state), 'unknown') AS global_runtime_status,
    COALESCE((SELECT conflict_state FROM authority_state), (SELECT authority_boundary FROM current_state), 'unknown') AS authority_boundary,
    COALESCE((SELECT status FROM patch_state), 'unknown') AS patch_status,
    CASE
        WHEN COALESCE((SELECT debt_count FROM debt_state), 0) = 0 THEN 'unknown'
        WHEN COALESCE((SELECT blocking_count FROM debt_state), 0) > 0 THEN 'blocking'
        WHEN COALESCE((SELECT open_or_partial_count FROM debt_state), 0) > 0 THEN 'partial'
        ELSE 'resolved'
    END AS debt_status,
    COALESCE((SELECT replay_reconciliation_state FROM replay_state), 'unknown') AS replay_reconciliation_state,
    COALESCE((SELECT replay_boundary_state FROM replay_state), 'unknown') AS replay_boundary_state,
    COALESCE((SELECT replay_subject_count FROM replay_state), 0) AS replay_subject_count,
    COALESCE((SELECT replay_event_count FROM replay_state), 0) AS replay_event_count,
    (SELECT replay_latest_subject_id FROM replay_state) AS replay_latest_subject_id,
    (SELECT replay_latest_subject_type FROM replay_state) AS replay_latest_subject_type,
    (SELECT replay_latest_event_id FROM replay_state) AS replay_latest_event_id,
    (SELECT replay_latest_event_type FROM replay_state) AS replay_latest_event_type,
    (SELECT replay_latest_source_patch_id FROM replay_state) AS replay_latest_source_patch_id,
    (SELECT replay_latest_source_path FROM replay_state) AS replay_latest_source_path,
    (SELECT replay_latest_created_at FROM replay_state) AS replay_latest_created_at,
    COALESCE((SELECT reason FROM authority_state), (SELECT latest_decision_reason FROM current_state), '') AS warnings,
    COALESCE((SELECT debt_ids FROM debt_state), '') AS minimal_evidence_paths,
    COALESCE((SELECT coverage_state FROM current_state), 'bootstrap') AS coverage_state;
