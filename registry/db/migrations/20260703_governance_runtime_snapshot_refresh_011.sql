-- Governance runtime snapshot-refresh migration.
-- Records explicit refresh attempts and the marker consumed by the freshness gate.

CREATE TABLE IF NOT EXISTS db_snapshot_refresh_metadata (
    scope TEXT PRIMARY KEY,
    refresh_id TEXT NOT NULL,
    last_refresh_attempt TIMESTAMP NOT NULL,
    last_refresh_result TEXT NOT NULL,
    indexed_at TIMESTAMP,
    source_worktree_marker TIMESTAMP,
    error_reason TEXT,
    registry_count INTEGER DEFAULT 0,
    indexed_registry_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW IF NOT EXISTS db_snapshot_refresh_view AS
SELECT
    scope,
    refresh_id,
    last_refresh_attempt,
    last_refresh_result,
    indexed_at,
    source_worktree_marker,
    error_reason,
    registry_count,
    indexed_registry_count,
    updated_at
FROM db_snapshot_refresh_metadata
WHERE scope = 'global';
