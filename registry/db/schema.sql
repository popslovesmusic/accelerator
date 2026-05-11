-- SQLite schema for the acellorator indexing layer
-- Role: Index, projection, provenance, and orientation mapping.
-- NOT a source of truth for semantics or claims.

CREATE TABLE IF NOT EXISTS orientation_status_types (
    status TEXT PRIMARY KEY,
    weight REAL DEFAULT 0.0,
    description TEXT
);

INSERT OR IGNORE INTO orientation_status_types (status, weight, description) VALUES
('current_command_evidence', 1.0, 'Data produced by the immediate active command.'),
('canonical_active', 0.95, 'Primary governance and truth files.'),
('active_runtime', 0.9, 'Scripts and tools currently used in production.'),
('unverified_residue', 0.45, 'Artifacts of unknown status/origin.'),
('historical_residue', 0.35, 'Prior findings or data that is no longer authoritative.'),
('archived', 0.25, 'Intentionally preserved historical data.'),
('deprecated', 0.15, 'Active but scheduled for removal or replacement.'),
('superseded', 0.1, 'Replaced by a newer version.'),
('invalidated', 0.0, 'Explicitly marked as incorrect or non-compliant.');

CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    artifact_type TEXT,
    orientation_status TEXT NOT NULL,
    authority_scope TEXT DEFAULT 'unknown',
    evidence_confidence TEXT DEFAULT 'not_checked',
    created_at TIMESTAMP,
    modified_at TIMESTAMP,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum TEXT,
    source_hash TEXT,
    metadata JSON,
    FOREIGN KEY (orientation_status) REFERENCES orientation_status_types(status)
);

CREATE TABLE IF NOT EXISTS audit_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT UNIQUE NOT NULL,
    path TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    task_id TEXT,
    report_type TEXT,
    evidence_orientation TEXT NOT NULL,
    verification_status TEXT,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_hash TEXT,
    summary TEXT,
    metadata JSON,
    FOREIGN KEY (evidence_orientation) REFERENCES orientation_status_types(status)
);

CREATE TABLE IF NOT EXISTS tool_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL,
    tool_path TEXT,
    status TEXT NOT NULL,
    evidence_source_path TEXT,
    command_used TEXT,
    raw_output_excerpt TEXT,
    certification_level TEXT,
    last_check TIMESTAMP NOT NULL,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_log TEXT,
    metadata JSON
);

CREATE TABLE IF NOT EXISTS registry_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registry_path TEXT NOT NULL,
    registry_type TEXT,
    source_hash TEXT NOT NULL,
    key_count INTEGER,
    modified_at TIMESTAMP,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    orientation_status TEXT NOT NULL,
    version TEXT,
    timestamp TIMESTAMP,
    snapshot_path TEXT
);

CREATE TABLE IF NOT EXISTS claim_evidence_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    orientation_status TEXT NOT NULL,
    FOREIGN KEY (orientation_status) REFERENCES orientation_status_types(status)
);

CREATE TABLE IF NOT EXISTS supersession_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_artifact_id INTEGER NOT NULL,
    to_artifact_id INTEGER NOT NULL,
    relation TEXT NOT NULL,
    evidence_path TEXT,
    confidence TEXT DEFAULT 'weak',
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_artifact_id) REFERENCES artifacts(id),
    FOREIGN KEY (to_artifact_id) REFERENCES artifacts(id)
);

CREATE INDEX IF NOT EXISTS idx_artifacts_path ON artifacts(path);
CREATE INDEX IF NOT EXISTS idx_artifacts_status ON artifacts(orientation_status);
CREATE INDEX IF NOT EXISTS idx_audit_reports_report_id ON audit_reports(report_id);
