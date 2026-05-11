# Database Projection Layer

This directory contains the SQLite database and schema used to index the acellorator platform.

## Role & Constraints

- **Role:** Artifact index, audit report index, tool health snapshot index, registry snapshot metadata, provenance map, orientation status map, and retrieval accelerator.
- **SSOT Constraint:** This database is **NOT** a source of truth for semantics, lexicon definitions, or claim status. Canonical authority remains in the JSON registries (e.g., `registry/lexicon_canonical.json`, `registry/claim_registry.json`).
- **Orientation:** All indexed artifacts must be assigned an `orientation_status` to distinguish between active truth and historical residue.

## Schema

See `schema.sql` for table definitions.

- `artifacts`: Filesystem index with orientation metadata.
- `audit_reports`: Registry of generated system audits.
- `tool_health`: Snapshots of tool certification and runtime status.
- `registry_snapshots`: Metadata about point-in-time registry states.
- `claim_evidence_links`: Mapping between claims and their supporting evidence artifacts.
- `supersession_edges`: Explicit tracking of which artifacts supersede others.

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

### Report Ingestion

Saved audit and health reports are indexed via:

```bash
python scripts/db/ingest_reports.py
```

### Tool Health Extraction

Tool certification and status summaries are extracted from reports via:

```bash
python scripts/db/ingest_tool_health.py
```

### Supersession Detection

Shadow, backup, and legacy relationships are detected and linked via:

```bash
python scripts/db/build_supersession_edges.py --apply
```

### Supersession Edge Confidence & Audit

`supersession_edges` are **advisory lineage metadata**. They help retrieval and maintenance planning but are not SSOT.

Confidence levels:

- `verified`: Direct current evidence identifies one artifact as superseding another (e.g., explicit declaration or governed registry authority recorded in `evidence_path`).
- `probable`: Strong filename/path/version relationship supports lineage but no direct declaration.
- `weak`: Pattern-only suggestion (useful as a hint; do not over-trust).

To audit supersession edge quality (missing refs, self-edges, duplicates, 2-cycles, confidence ratios):

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

Read-only traceability reports linking registry entries to runtime artifacts, validation files, and DB rows can be generated via:

```bash
python scripts/registry_runtime_trace.py --query <topic>
```

Gemini context packets for traceability reasoning:

```bash
python scripts/gemini_trace_context.py --query <topic>
```

**Boundary:** Traceability is observational and advisory. It must not override SSOT registries or promote claims automatically.

## Governance Boundary

**CRITICAL:** This database is a **PROJECTION LAYER** only.

- Ingestion indexes and links evidence; it does not promote claims or terms.
- Registry snapshots record metadata; they do not replace JSON registries as SSOT.
- Supersession edges are advisory; they do not move or delete files.
- If the database conflicts with a canonical registry, the registry wins.

## Orientation-Aware Retrieval

The retrieval layer (`scripts/orientation_retrieval.py`) ranks artifacts by **admissible relevance** rather than just text similarity or timestamp.

### Scoring Model

Score is calculated as:
`score = 0.35*orientation_status + 0.25*authority_scope + 0.20*evidence_confidence + 0.10*freshness + 0.10*text_match`

- **Orientation Status:** Prioritizes `current_command_evidence` and `canonical_active`.
- **Authority Scope:** Prioritizes `lexicon` and `registry` files.
- **Evidence Confidence:** Prioritizes `verified` artifacts.
- **Freshness:** Decay based on time since indexing/modification.
- **Text Match:** Keyword matching on path/filename.

### Usage

```bash
python scripts/orientation_retrieval.py --query graph_dynamics --explain
```

**Note:** Retrieval rankings are advisory. They must not override the SSOT registries or the compliance charter.

When `--explain` is used and `supersession_edges` are present, retrieval includes advisory lineage diagnostics per-result (relation/confidence counts, pattern-only warnings, and cycle-risk warnings). These cautions must not be used as authority for deletion, suppression, or overriding canonical registries.
