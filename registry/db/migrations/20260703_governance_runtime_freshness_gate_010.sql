-- Governance runtime freshness gate migration.
-- Projects DB snapshot recency without replacing the runtime-side freshness decision logic.

DROP VIEW IF EXISTS db_snapshot_freshness_view;

CREATE VIEW db_snapshot_freshness_view AS
SELECT
    (SELECT MAX(indexed_at) FROM artifacts) AS indexed_at,
    CASE
        WHEN (SELECT MAX(indexed_at) FROM artifacts) IS NULL THEN 'unknown'
        WHEN julianday('now') - julianday((SELECT MAX(indexed_at) FROM artifacts)) > 14 THEN 'stale'
        ELSE 'fresh'
    END AS db_snapshot_status,
    CASE
        WHEN (SELECT MAX(indexed_at) FROM artifacts) IS NULL THEN NULL
        ELSE CAST(julianday('now') - julianday((SELECT MAX(indexed_at) FROM artifacts)) AS INTEGER)
    END AS snapshot_age_days,
    CASE
        WHEN (SELECT MAX(indexed_at) FROM artifacts) IS NULL THEN 'unavailable'
        WHEN julianday('now') - julianday((SELECT MAX(indexed_at) FROM artifacts)) > 14 THEN 'refresh_required'
        ELSE 'fresh_within_threshold'
    END AS freshness_class,
    'db_projection' AS coverage_state,
    'DB snapshot freshness is projected from indexed artifact timestamps; worktree recency is assessed by the runtime gate.' AS rule_text;
