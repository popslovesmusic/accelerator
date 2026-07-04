CREATE TABLE IF NOT EXISTS semantic_authority_map (
    semantic_key TEXT PRIMARY KEY NOT NULL,
    semantic_type TEXT NOT NULL,
    authority_source TEXT NOT NULL,
    authority_rank TEXT NOT NULL,
    supersedes TEXT,
    status TEXT NOT NULL,
    canonical_expression TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_semantic_authority_map_type
    ON semantic_authority_map(semantic_type);

CREATE INDEX IF NOT EXISTS idx_semantic_authority_map_rank
    ON semantic_authority_map(authority_rank);

CREATE INDEX IF NOT EXISTS idx_semantic_authority_map_status
    ON semantic_authority_map(status);

CREATE INDEX IF NOT EXISTS idx_semantic_authority_map_source
    ON semantic_authority_map(authority_source);

CREATE TABLE IF NOT EXISTS semantic_authority_events (
    event_id TEXT PRIMARY KEY NOT NULL,
    semantic_key TEXT NOT NULL,
    event_type TEXT NOT NULL,
    authority_source TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_semantic_authority_events_key
    ON semantic_authority_events(semantic_key);

CREATE INDEX IF NOT EXISTS idx_semantic_authority_events_type
    ON semantic_authority_events(event_type);

CREATE INDEX IF NOT EXISTS idx_semantic_authority_events_created_at
    ON semantic_authority_events(created_at);

DROP VIEW IF EXISTS semantic_authority_view;

CREATE VIEW semantic_authority_view AS
SELECT
    semantic_key,
    semantic_type,
    authority_source,
    authority_rank,
    supersedes,
    status,
    canonical_expression,
    notes,
    created_at,
    updated_at
FROM semantic_authority_map;

INSERT OR IGNORE INTO semantic_authority_map (
    semantic_key,
    semantic_type,
    authority_source,
    authority_rank,
    supersedes,
    status,
    canonical_expression,
    notes
) VALUES
    (
        'RT_CORE',
        'theorem',
        'registry/theorem_registry.json',
        'canonical',
        NULL,
        'active',
        'RT := [(ℰ≠0) ⇔R δα(ℰ>0)]',
        'Canonical whole-expression RT binding used by the semantic authority runtime.'
    ),
    (
        'META_A_BINDING',
        'operator_binding',
        'registry/theorem_registry.json',
        'canonical',
        NULL,
        'active',
        'A_meta := δα(ℰ>0)',
        'Canonical meta-domain A binding used by the semantic authority runtime.'
    ),
    (
        'META_B_BINDING',
        'operator_binding',
        'registry/theorem_registry.json',
        'canonical',
        NULL,
        'active',
        'B_meta := (ℰ≠0)',
        'Canonical meta-domain B binding used by the semantic authority runtime.'
    ),
    (
        'REGISTRY_AUTHORITY_PRINCIPLE',
        'runtime_rule',
        'registry/governance_change_ledger.json',
        'canonical',
        NULL,
        'active',
        'Registry remains canonical authority; DB runtime is operational projection.',
        'Registry authority remains canonical while the DB runtime acts as the operational gate.'
    ),
    (
        'DB_RUNTIME_ROLE',
        'runtime_rule',
        'registry/db/README.md',
        'primary',
        NULL,
        'active',
        'Database provides executable governance and runtime decision support.',
        'The DB runtime is the primary executable governance projection.'
    );
