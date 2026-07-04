-- Governance runtime debt-view migration.
-- Adds a runtime-facing debt projection synchronized from the governed debt registry.

DROP VIEW IF EXISTS debt_runtime_view;

CREATE TABLE IF NOT EXISTS debt_runtime_projection (
    debt_id TEXT PRIMARY KEY,
    title TEXT,
    department TEXT,
    status TEXT,
    severity TEXT,
    domain TEXT,
    blocking_scope TEXT,
    owner_surface TEXT,
    resolution_patch TEXT,
    decision_effect TEXT,
    evidence_paths TEXT,
    warnings TEXT,
    source_path TEXT,
    introduced_by TEXT,
    affects TEXT,
    blocks TEXT,
    depends_on TEXT,
    required_resolution TEXT,
    raw_status TEXT,
    raw_severity TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW debt_runtime_view AS
SELECT
    debt_id,
    title,
    department,
    status,
    severity,
    domain,
    blocking_scope,
    owner_surface,
    resolution_patch,
    decision_effect,
    evidence_paths,
    warnings,
    source_path,
    introduced_by,
    affects,
    blocks,
    depends_on,
    required_resolution,
    raw_status,
    raw_severity,
    updated_at,
    'registry_projection' AS coverage_state
FROM debt_runtime_projection;
