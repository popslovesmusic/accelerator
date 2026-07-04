CREATE VIEW IF NOT EXISTS governance_event_count_by_subject_view AS
SELECT
    subject_id,
    subject_type,
    COUNT(*) AS event_count,
    MAX(COALESCE(created_at, '')) AS latest_created_at
FROM governance_events
GROUP BY subject_id, subject_type;

CREATE VIEW IF NOT EXISTS governance_event_latest_by_subject_view AS
SELECT
    event_id,
    event_type,
    subject_id,
    subject_type,
    source_patch_id,
    source_path,
    payload_json,
    evidence_paths_json,
    created_at,
    event_count
FROM (
    SELECT
        governance_events.*,
        COUNT(*) OVER (PARTITION BY subject_id, subject_type) AS event_count,
        ROW_NUMBER() OVER (
            PARTITION BY subject_id, subject_type
            ORDER BY COALESCE(created_at, '') DESC, event_id DESC
        ) AS row_rank
    FROM governance_events
)
WHERE row_rank = 1;
