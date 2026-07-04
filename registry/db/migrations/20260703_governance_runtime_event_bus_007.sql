-- Governance runtime event-bus migration.
-- Adds an append-only event surface for governance-significant facts.

CREATE TABLE IF NOT EXISTS governance_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    source_patch_id TEXT,
    source_path TEXT,
    payload_json TEXT NOT NULL DEFAULT '{}',
    evidence_paths_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_governance_events_event_type
    ON governance_events(event_type);

CREATE INDEX IF NOT EXISTS idx_governance_events_subject_id
    ON governance_events(subject_id);

CREATE INDEX IF NOT EXISTS idx_governance_events_source_patch_id
    ON governance_events(source_patch_id);

CREATE INDEX IF NOT EXISTS idx_governance_events_created_at
    ON governance_events(created_at);
