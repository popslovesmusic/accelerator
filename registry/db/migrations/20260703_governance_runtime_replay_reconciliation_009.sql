CREATE VIEW IF NOT EXISTS governance_replay_reconciliation_view AS
SELECT
    l.subject_id,
    l.subject_type,
    l.event_id AS latest_event_id,
    l.event_type AS latest_event_type,
    l.source_patch_id AS latest_source_patch_id,
    l.source_path AS latest_source_path,
    c.event_count,
    c.latest_created_at
FROM governance_event_latest_by_subject_view AS l
LEFT JOIN governance_event_count_by_subject_view AS c
    ON c.subject_id = l.subject_id
   AND c.subject_type = l.subject_type;
