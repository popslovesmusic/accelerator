-- Governance runtime authority-resolution migration.
-- Adds a target-aware authority catalog for governed surfaces.

DROP VIEW IF EXISTS authority_resolution_view;

CREATE VIEW authority_resolution_view AS
SELECT
    'registry/governance_change_ledger.json' AS target_pattern,
    'registry' AS authority_owner,
    'registry/governance_change_ledger.json' AS authority_source,
    'current' AS supersession_status,
    '[]' AS superseded_by,
    'clear' AS conflict_state,
    'allow' AS decision,
    'The governance change ledger is the canonical registry authority for live governance changes.' AS reason,
    '["registry/governance_change_ledger.json","docs/governance/GLOBAL_VALIDATION_ROUTINE.md"]' AS evidence_paths,
    '[]' AS warnings
UNION ALL
SELECT
    'registry/research_debt_registry.json' AS target_pattern,
    'registry' AS authority_owner,
    'registry/research_debt_registry.json' AS authority_source,
    'current' AS supersession_status,
    '[]' AS superseded_by,
    'clear' AS conflict_state,
    'allow' AS decision,
    'The research debt registry is the canonical registry authority for open and partially resolved governance debt.' AS reason,
    '["registry/research_debt_registry.json","docs/governance/GLOBAL_VALIDATION_ROUTINE.md"]' AS evidence_paths,
    '[]' AS warnings
UNION ALL
SELECT
    'registry/governance/patches/PATCH_DB_GOVERNANCE_RUNTIME_003.json' AS target_pattern,
    'registry' AS authority_owner,
    'registry/governance/patches/PATCH_DB_GOVERNANCE_RUNTIME_003.json' AS authority_source,
    'current' AS supersession_status,
    '[]' AS superseded_by,
    'clear' AS conflict_state,
    'allow' AS decision,
    'Patch registry entries remain governed registry surfaces and are writable only through governed change paths.' AS reason,
    '["registry/governance_change_ledger.json","docs/governance/GLOBAL_VALIDATION_ROUTINE.md"]' AS evidence_paths,
    '[]' AS warnings
UNION ALL
SELECT
    'registry/db/migrations/20260703_governance_runtime_bootstrap_001.sql' AS target_pattern,
    'db_runtime' AS authority_owner,
    'registry/db/migrations/20260703_governance_runtime_bootstrap_001.sql' AS authority_source,
    'superseded' AS supersession_status,
    '["registry/db/migrations/20260703_governance_runtime_current_state_002.sql","registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql"]' AS superseded_by,
    'stale' AS conflict_state,
    'defer' AS decision,
    'The bootstrap migration is superseded by later runtime migrations and should not be treated as the live authority surface.' AS reason,
    '["registry/db/migrations/20260703_governance_runtime_current_state_002.sql","registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql"]' AS evidence_paths,
    '["Use the later runtime migrations instead of the bootstrap surface."]' AS warnings
UNION ALL
SELECT
    'registry/db/migrations/20260703_governance_runtime_current_state_002.sql' AS target_pattern,
    'db_runtime' AS authority_owner,
    'registry/db/migrations/20260703_governance_runtime_current_state_002.sql' AS authority_source,
    'current' AS supersession_status,
    '[]' AS superseded_by,
    'clear' AS conflict_state,
    'allow' AS decision,
    'The current-state migration is the live runtime projection for state queries.' AS reason,
    '["registry/db/migrations/20260703_governance_runtime_current_state_002.sql","registry/db/README.md"]' AS evidence_paths,
    '[]' AS warnings
UNION ALL
SELECT
    'registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql' AS target_pattern,
    'db_runtime' AS authority_owner,
    'registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql' AS authority_source,
    'current' AS supersession_status,
    '[]' AS superseded_by,
    'clear' AS conflict_state,
    'allow' AS decision,
    'The authority-resolution migration is the live runtime projection for ownership and supersession queries.' AS reason,
    '["registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql","registry/db/README.md"]' AS evidence_paths,
    '[]' AS warnings
UNION ALL
SELECT
    'registry/math_source_registry.json' AS target_pattern,
    'registry' AS authority_owner,
    'registry/math_source_registry.json' AS authority_source,
    'current' AS supersession_status,
    '[]' AS superseded_by,
    'clear' AS conflict_state,
    'allow' AS decision,
    'The math source registry is the canonical registry source for foundational mathematical documents and provenance.' AS reason,
    '["registry/math_source_registry.json","docs/math/codex_master_index.md"]' AS evidence_paths,
    '[]' AS warnings
UNION ALL
SELECT
    'registry/math_registry.json' AS target_pattern,
    'registry' AS authority_owner,
    'registry/math_source_registry.json' AS authority_source,
    'superseded' AS supersession_status,
    '["registry/math_source_registry.json"]' AS superseded_by,
    'deprecated' AS conflict_state,
    'defer' AS decision,
    'The legacy math registry name is deprecated in favor of registry/math_source_registry.json.' AS reason,
    '["registry/math_source_registry.json","docs/math/codex_master_index.md","docs/math/open_questions_map.md"]' AS evidence_paths,
    '["Use registry/math_source_registry.json instead."]' AS warnings
UNION ALL
SELECT
    'scripts/query_governance.py' AS target_pattern,
    'db_runtime' AS authority_owner,
    'scripts/query_governance.py' AS authority_source,
    'current' AS supersession_status,
    '[]' AS superseded_by,
    'clear' AS conflict_state,
    'allow' AS decision,
    'The query_governance runtime script is part of the live DB governance gate implementation.' AS reason,
    '["scripts/query_governance.py","registry/db/migrations/20260703_governance_runtime_current_state_002.sql","registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql"]' AS evidence_paths,
    '[]' AS warnings
UNION ALL
SELECT
    'registry/db/README.md' AS target_pattern,
    'registry' AS authority_owner,
    'registry/db/README.md' AS authority_source,
    'current' AS supersession_status,
    '[]' AS superseded_by,
    'clear' AS conflict_state,
    'allow' AS decision,
    'The DB README is a governed registry document that describes the live runtime surfaces.' AS reason,
    '["registry/db/README.md","docs/governance/GLOBAL_VALIDATION_ROUTINE.md"]' AS evidence_paths,
    '[]' AS warnings
UNION ALL
SELECT
    'docs/governance/GLOBAL_VALIDATION_ROUTINE.md' AS target_pattern,
    'docs' AS authority_owner,
    'docs/governance/GLOBAL_VALIDATION_ROUTINE.md' AS authority_source,
    'current' AS supersession_status,
    '[]' AS superseded_by,
    'clear' AS conflict_state,
    'allow' AS decision,
    'Governance documentation remains the narrative authority for procedural guidance.' AS reason,
    '["docs/governance/GLOBAL_VALIDATION_ROUTINE.md","outputs/audits/global_health_report.json"]' AS evidence_paths,
    '[]' AS warnings
UNION ALL
SELECT
    'docs/textbook/mono_process_textbook_complete.md' AS target_pattern,
    'textbook' AS authority_owner,
    'docs/textbook/mono_process_textbook_complete.md' AS authority_source,
    'current' AS supersession_status,
    '[]' AS superseded_by,
    'clear' AS conflict_state,
    'allow' AS decision,
    'The textbook remains the long-form narrative authority and is not replaced by runtime projections.' AS reason,
    '["docs/textbook/mono_process_textbook_complete.md","docs/governance/GLOBAL_VALIDATION_ROUTINE.md"]' AS evidence_paths,
    '[]' AS warnings;
