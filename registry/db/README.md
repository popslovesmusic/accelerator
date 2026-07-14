# Database Projection Layer

This directory contains the SQLite database and schema used to index the acellorator platform.

## Role & Constraints

- **Role:** Artifact index, audit report index, tool health snapshot index, registry snapshot metadata, provenance map, orientation status map, and retrieval accelerator.
- **SSOT Constraint:** This database is **NOT** a source of truth for semantics, lexicon definitions, or claim status. Canonical authority remains in the JSON registries (e.g., `registry/lexicon_canonical.json`, `registry/claim_registry.json`).
- **Orientation:** All indexed artifacts must be assigned an `orientation_status` to distinguish between active truth and historical residue.
- **Governance Runtime Bootstrap:** The DB is now also the first-pass governance gate for patch/application decisions. When it cannot classify an action, fall back to registries and long-form docs rather than treating document-first routing as the default.

## Schema

See `schema.sql` for table definitions.

- `artifacts`: Filesystem index with orientation metadata.
- `audit_reports`: Registry of generated system audits.
- `tool_health`: Snapshots of tool rigor endorsement and runtime status.
- `registry_snapshots`: Metadata about point-in-time registry states.
- `claim_evidence_links`: Mapping between claims and their supporting evidence artifacts.
- `supersession_edges`: Explicit tracking of which artifacts supersede others.
- `compressed_residue`: Metadata for governed semantic summaries.
- `governance_decision_log`: Patch/application decisions, reasons, and evidence basis for the runtime gate.
- `governance_events`: Append-only governance-significant facts captured by the runtime event bus.
- `governance_event_latest_by_subject_view`: Latest append-only event per subject for bounded diagnostic replay.
- `governance_event_count_by_subject_view`: Event count per subject for replay and coverage diagnostics.
- `governance_replay_reconciliation_view`: Subject-level replay coverage metadata used for diagnostic comparison and capsule summaries.
- `semantic_authority_map`: Semantic claims, concepts, operators, theorem bindings, and runtime-rule authority records.
- `semantic_authority_events`: Append-only semantic authority change history.

The initial semantic authority seed is mirrored in `registry/theorem_registry.json` and projected into the DB runtime from there.

## Orientation Status Values

- `current_command_evidence`: Data produced by the immediate active command.
- `canonical_active`: Primary governance and truth files.
- `active_runtime`: Scripts and tools currently used in production.
- `historical_residue`: Prior findings or data that is no longer authoritative.
- `archived`: Intentionally preserved historical data.
- `deprecated`: Active but scheduled for removal or replacement.
- `superseded`: Replaced by a newer version.
- `invalidated`: Explicitly marked as incorrect or non-compliant.
- `unverified_residue`: Artifacts of unknown status/origin.

## Ingestion & Population

The projection layer is populated by ingesting evidence artifacts and registry metadata.

### Registry Snapshots

Metadata about canonical registries (hash, key counts) is captured via:

```bash
python scripts/db/snapshot_registries.py
```

The refresh command now writes a single `db_snapshot_refresh_metadata` record consumed by the freshness gate. It emits a structured result that includes `status`, `last_refresh_attempt`, `last_refresh_result`, `indexed_at`, `source_worktree_marker`, `runtime_worktree_marker`, `indexed_registry_count`, `missing_registries`, and `error_reason`.

Freshness reads the latest verified refresh marker first. Source-affecting registry, doc, and script changes still stale the snapshot, but runtime-only DB churn such as decision logs, event writes, and other append-only runtime surfaces is compared against the stored runtime marker and reported separately as `runtime_churn` when it is newer. A fresh snapshot can therefore remain `fresh` or `allow_with_note` after routine runtime writes, while genuine source drift still reports `source_change` and refresh failures remain `unknown`.

### Report Ingestion

Saved audit and health reports are indexed via:

```bash
python scripts/db/ingest_reports.py
```

### Tool Health Extraction

Tool rigor endorsement and status summaries are extracted from reports via:

```bash
python scripts/db/ingest_tool_health.py
```

### Supersession Detection

Explicit supersession declarations in governed source artifacts are linked via:

```bash
python scripts/db/build_supersession_edges.py --apply
```

The builder backfills missing `docs/**/*.md` and `registry/**/*.md` artifact rows before rebuilding the graph, then emits only explicit lineage edges it can resolve to real indexed artifacts.

### Supersession Edge Confidence & Audit

`supersession_edges` are **advisory lineage metadata**. They help retrieval and maintenance planning but are not SSOT.

Confidence levels:

- `verified`: Direct current evidence identifies one artifact as superseding another.
- `probable`: Reserved for future curated heuristics; not emitted by the current builder.
- `weak`: Reserved for future low-confidence suggestions; not emitted by the current builder.

To audit supersession edge quality:

```bash
python scripts/db/audit_supersession_edges.py --db registry/db/acellorator_index.sqlite --sample 50
```

## Claim-Evidence Graph

A read-only graph view of research metadata (claims, tools, reports, artifacts) is available via:

```bash
python scripts/claim_evidence_graph.py
```

Reasoning context for Gemini can be generated using:

```bash
python scripts/gemini_claim_context.py --query <topic>
```

## Execution Planning

Advisory execution plans ranked by orientation-aware evidence and governance constraints can be generated via:

```bash
python scripts/orientation_execution_plan.py --query <task>
```

**Note:** Execution plans are advisory only. Actual execution requires separate authorization.

## Registry-to-Runtime Traceability

Read-only traceability reports linking registry entries to runtime artifacts, validation files, and DB rows:

```bash
python scripts/registry_runtime_trace.py --query <topic>
```

Gemini context packets for traceability reasoning:

```bash
python scripts/gemini_trace_context.py --query <topic>
```

## Governed Agent Memory

Orientation-aware agent memory for reasoning and maintenance context:

```bash
python scripts/gemini_memory_context.py --query <topic>
python scripts/codex_memory_context.py --query <topic>
```

Memory health and boundary validation:

```bash
python scripts/agent_memory/memory_health_check.py
```

## Cross-Tool Causal Provenance

Observational lineage mapping across claims, artifacts, and tools:

```bash
python scripts/provenance/provenance_query.py --query <topic>
```

Provenance health and cycle detection:

```bash
python scripts/provenance/provenance_health_check.py
```

Reasoning context for Gemini/Codex:

```bash
python scripts/provenance/provenance_packet_builder.py --query <topic>
```

## Semantic Residue Compression

Lossy context reduction for large historical research chains:

```bash
python scripts/residue/compress_residue.py --query <topic> --out outputs/reports/residue_summary.json
```

Query and health check:

```bash
python scripts/residue/residue_query.py --query <topic>
python scripts/residue/residue_health_check.py --path <path>
```

## Formal Object Ontology

Provisional mathematical scaffolding for process mathematics:

```bash
python scripts/math/validate_formal_objects.py
python scripts/math/object_dependency_trace.py --query <topic>
```
Registries:
- `registry/formal_objects/formal_object_registry.json`
- `registry/math/operator_registry.json`
- `registry/math/relation_registry.json`
- `registry/math/object_axiom_scaffold.json`

## Formal Reduction Chains

Advisory trace scaffolds connecting high-level expressions to primitives:

```bash
python scripts/math/validate_reduction_chains.py
python scripts/math/reduction_chain_trace.py --query <expression>
```

Registries:
- `registry/math/reduction_chain_registry.json`
- `registry/math/primitive_dependency_registry.json`
- `registry/math/derivation_status_registry.json`
- `registry/math/reduction_gap_registry.json`

**Boundary:** Reduction chains are formal trace artifacts and do not assert physical truth.

## Governance Boundary

**Boundary:** Formal scaffolding is provisional and does not assert physical truth.

## Governance Boundary


The projection layer includes automated health and maintenance utilities.

### Health Check

Integrity, schema, and retrieval readiness are verified via a fast routine check:

```bash
python scripts/db/db_health_check.py
```

Use the maintenance command when you explicitly need the slower exhaustive SQLite scan:

```bash
python scripts/db/db_maintenance.py --report-only --full-integrity-check
```

DB health is also integrated into `scripts/global_validate.py`.

### Maintenance

Routine diagnostics and non-mutating cleanup:

```bash
python scripts/db/db_maintenance.py --report-only
```

Add `--full-integrity-check` when you need the exhaustive scan:

```bash
python scripts/db/db_maintenance.py --report-only --full-integrity-check
```

Mutating operations (VACUUM, ANALYZE) require explicit flags:

```bash
python scripts/db/db_maintenance.py --mutate
```

## Governance Boundary

**CRITICAL:** This database is a **PROJECTION LAYER** only.

- Ingestion indexes and links evidence; it does not promote claims or terms.
- Registry snapshots record metadata; they do not replace JSON registries as SSOT.
- Supersession edges are advisory; they do not move or delete files.
- Memory and compression are contextual aids; they do not redefine lexicon meaning or claim status.
- If the database conflicts with a canonical registry, the registry wins.
- Document-first retrieval is fallback only when the DB runtime cannot classify the action or when a long-form narrative is explicitly needed.

## Governance Runtime Gate

Patch/application decisions should be queried through the bootstrap runtime first.

To inspect the live state capsule before opening broad documentation surfaces:

```bash
python scripts/query_governance.py current-state
```

To inspect snapshot freshness before DB-dependent operations:

```bash
python scripts/query_governance.py freshness [--target <path-or-surface>] [--pretty]
```

To resolve live authority for a specific governed surface before editing it:

```bash
python scripts/query_governance.py authority --target <path-or-surface>
```

To resolve semantic authority for a theorem, operator binding, concept, claim, domain, or runtime rule:

```bash
python scripts/query_governance.py authority --semantic <key> --semantic-type <type>
```

To resolve patch dependency state before attempting application:

```bash
python scripts/query_governance.py patch-chain --patch-id <PATCH_ID>
```

To inspect governed debt before attempting application:

```bash
python scripts/query_governance.py debt --status <open|partial|resolved|blocking|all>
```

To generate the minimal agent-facing runtime capsule before broad document traversal:

```bash
python scripts/query_governance.py context-capsule [--target <path-or-surface>] [--task <label>]
```

To append a governance-significant event fact:

```bash
python scripts/query_governance.py emit-event --event-type <type> --subject-id <id> --subject-type <patch|debt|authority|validation|capsule|db_snapshot|runtime|unknown> --source-patch-id <PATCH_ID> --source-path <path> --payload-json '{"key":"value"}' [--evidence-path <path>]
```

To query recorded governance events:

```bash
python scripts/query_governance.py events [--event-type <type>] [--subject-id <id>] [--source-patch-id <PATCH_ID>] [--limit <n>]
```

To reconstruct a bounded diagnostic state from safe governance events:

```bash
python scripts/query_governance.py replay-events [--event-type <type>] [--subject-id <id>] [--limit <n>] [--pretty]
```

To compare replayed state against registry authority:

```bash
python scripts/query_governance.py reconcile-events [--subject-id <id>] [--patch-id <PATCH_ID>] [--event-type <type>] [--pretty]
```

To request an apply/block/defer decision for a specific patch:

```bash
python scripts/query_governance.py patch-gate --patch-id <PATCH_ID> --target <path-or-surface>
```

The runtime logs decisions to `governance_decision_log` when the migration has been applied or bootstrapped by the query command. The current-state projection is DB-backed; freshness is a separate DB-backed snapshot-age gate that ignores runtime-only DB churn and only treats source-affecting changes as freshness invalidators. Authority resolution is target-aware but still a gate, not a semantic SSOT, and the same runtime now also resolves semantic authority for declared concepts, claims, operators, theorem bindings, domains, and runtime rules. Patch-chain resolution is DB-backed through the decision log and registry patch records, but it is still a gate rather than a replacement for registry provenance. Debt runtime projections are now available through the `debt` command and are consulted by the patch gate after patch-chain and authority resolution. When a patch declares semantic targets, patch-gate consults the semantic authority map and records missing, superseded, or deprecated semantic authority as a governed decision condition instead of silently allowing it. The event bus is append-only and records governance-significant facts; it does not replace registry authority. `replay-events` reconstructs only a bounded diagnostic state from safe event types and remains non-authoritative. `reconcile-events` compares replayed state against registry authority and reports divergence only. The preferred runtime order is `context-capsule -> current-state -> freshness -> authority -> patch-chain -> debt -> patch-gate`, and `context-capsule` is the preferred runtime entrypoint for agents because it composes the minimal operational summary from current-state, freshness, authority, patch-chain, debt, recent events, a semantic authority graph summary, claim-registry / claim-support summaries, and bounded replay reconciliation coverage at request time. Open governance/runtime debt is still governed by the debt registry as the authoritative source of debt records. If `freshness` remains stale after `python scripts/db/snapshot_registries.py`, the cause is recorded explicitly in the command output and usually means source-affecting worktree files changed after the last verified refresh marker, not merely runtime logging.

## Orientation-Aware Retrieval

The retrieval layer (`scripts/orientation_retrieval.py`) ranks artifacts by **admissible relevance** rather than just text similarity or timestamp.

### Scoring Model

Score is calculated as:
`score = 0.35*orientation_status + 0.25*authority_scope + 0.20*evidence_confidence + 0.10*freshness + 0.10*text_match`

### Usage

```bash
python scripts/orientation_retrieval.py --query <query> --explain
```

**Note:** Retrieval rankings are advisory. They must not override the SSOT registries or the compliance charter.
