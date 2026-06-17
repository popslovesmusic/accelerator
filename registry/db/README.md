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
- `tool_health`: Snapshots of tool rigor endorsement and runtime status.
- `registry_snapshots`: Metadata about point-in-time registry states.
- `claim_evidence_links`: Mapping between claims and their supporting evidence artifacts.
- `supersession_edges`: Explicit tracking of which artifacts supersede others.
- `compressed_residue`: Metadata for governed semantic summaries.

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

Integrity, schema, and retrieval readiness are verified via:

```bash
python scripts/db/db_health_check.py
```

DB health is also integrated into `scripts/global_validate.py`.

### Maintenance

Routine diagnostics and non-mutating cleanup:

```bash
python scripts/db/db_maintenance.py --report-only
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
