# AI DB Retrieval Path Audit 2026-07-03

## Executive Summary

The repository does have a live SQLite projection layer, but it is not yet the default current-state retrieval path. The DB can answer some path-based queries, such as `global_health_report` and `mono_process`, but it does not answer semantic questions like `current RT` or `open debt` directly. In practice, agents are still routed through docs and registry files first, with DB helpers used opportunistically.

The right token-cost strategy is not "replace docs with DB". It is:

1. Route supported queries through the DB first.
2. Add the missing current-state views.
3. Keep long-form docs and the textbook as canonical narrative sources.

## DB Surfaces Found

| Surface | State | Notes |
| --- | --- | --- |
| `registry/db/acellorator_index.sqlite` | Live | Populated SQLite projection/index layer. Current snapshot is older than the current worktree. |
| `registry/db/schema.sql` | Live | Defines the live SQLite tables and status types. |
| `registry/db/README.md` | Live but stale in examples | Describes the DB as a retrieval accelerator and not a semantic SSOT. Some example paths are old. |
| `scripts/db/db_health_check.py` | Live | Checks table presence, orientation statuses, retrieval smoke, and supersession health. |
| `scripts/orientation_retrieval.py` | Live | Main retrieval entrypoint; ranks by status, scope, confidence, freshness, and text match. |
| `scripts/claim_evidence_graph.py` | Live | Builds claim/evidence/supersession graphs from the DB. |
| `scripts/gemini_*_context.py`, `scripts/codex_memory_context.py`, `scripts/orientation_execution_plan.py`, `scripts/registry_runtime_trace.py`, `scripts/provenance/provenance_query.py`, `scripts/residue/compress_residue.py` | Live helpers | Context and trace helpers built on DB retrieval or related projections. |
| `registry/sqlite_governance_index_manifest.json` | Stale path mismatch | Still points to `registry/db/pcd_governance.db` while the live file is `registry/db/acellorator_index.sqlite`. |
| `registry/sqlite_schema_v1.json` | Historical / alternate | Does not match the live SQLite schema. |
| `scripts/query_governance.py` | Scaffold | Placeholder rather than a functional entrypoint. |
| `scripts/assemble_governed_context.py` | Scaffold | Still a stub that comments about querying `pcd_governance.db`. |

The live DB snapshot is not small: it contains 21,242 artifacts, 22 audit reports, 73 supersession edges, 39 tool health rows, and 7 registry snapshots. But `claim_evidence_links` and `compressed_residue` are both empty, which is a strong sign that the DB is still a projection layer rather than a complete knowledge-state engine.

## Current Agent Retrieval Path

I found no explicit repo-wide instruction that says "query the DB first." The existing routing still favors filesystem and docs-based workflows:

- `AGENTS.md` requires current governance checks and textbook synchronization.
- `docs/AGENTS.md` frames documentation work around report writing and validation.
- `docs/governance/GLOBAL_VALIDATION_ROUTINE.md` requires the latest `outputs/audits/global_health_report.json`.
- `registry/governed_context_assembly_registry.json` uses `docs/tech_notes` together with `pcd_governance.db` only for specific packet types.
- `scripts/query_governance.py` and `scripts/assemble_governed_context.py` are still scaffolds.

So the observed default path is:

`docs and registry files -> validation reports -> optional DB helper scripts`

not:

`DB first -> minimal context capsule -> docs only when needed`

## Can the DB Answer Current-State Questions?

| Query | Result | Interpretation |
| --- | --- | --- |
| `global_health_report` | Pass | The DB can retrieve a current-state artifact path when the artifact is indexed. |
| `mono_process` | Pass | The DB can retrieve doc artifacts by keyword/path, but this is still document retrieval. |
| `current RT` | Fail: no results | The DB does not answer the semantic current-state question directly. |
| `open debt` | Fail: no results | The DB does not currently surface debt state directly. |
| `current authoritative files` | Fail: no results | The DB does not provide an authority view that can answer this without broader scanning. |

Conclusion: the DB can answer some retrieval questions, but it is not yet a current-state answer engine.

## Catalog vs Knowledge-State Assessment

The DB is more than a plain catalog. It already stores orientation status, authority scope, evidence confidence, supersession edges, and tool health. That makes it a real projection layer, not just a path list.

However, it still falls short of a knowledge-state layer because:

- the link tables that would support claim-to-evidence reasoning are empty;
- residue compression is not populated;
- there is no first-class view for current state, authority, patch chains, debt, or induction readiness;
- the retrieval helper is keyword/path based rather than semantic/current-state based.

So the correct classification is:

`projection layer with state annotations, not yet a complete knowledge-state layer`

## Why the Prior Audit Became Document-Centric

The prior audit was not wrong. It was scoped around document surfaces, and the repository itself still encourages that behavior.

The main reasons are:

- governance instructions still refer to docs, textbook synchronization, and global health reports;
- the DB is explicitly not the SSOT for semantics, lexicon definitions, or claim status;
- the live DB index is stale relative to the current worktree;
- some DB-facing files still use the older `pcd_governance.db` naming convention;
- some DB-facing scripts remain scaffolds rather than operational entrypoints.

## Recommended Patch Plan

1. Add an explicit DB-first retrieval rule to governing agent instructions.
2. Create a `current_state_view` that answers current RT, active files, and current claim gates.
3. Create an `authority_view` that resolves live authority, supersession, and canonical ownership.
4. Create a `patch_chain_view` for active, blocked, missing, and late-registered patch state.
5. Create a `debt_view` for governance, math, lexicon, induction, documentation, and research debt.
6. Create an `induction_view` for departmental readiness and backlog state.
7. Create a `historical_residue_view` that cleanly separates live state from archived or superseded state.
8. Create an `agent_context_capsule_view` that returns the minimum authoritative context needed for an action.
9. Implement `scripts/query_governance.py` and `scripts/assemble_governed_context.py` beyond scaffold mode.
10. Reconcile the `pcd_governance.db` naming convention with `acellorator_index.sqlite`.

This is not a rewrite of the docs strategy. It is a routing and projection upgrade that would let the DB cut context cost before the agent opens broad Markdown surfaces.

## Bottom Line

The repository is **not DB-first today**.

The DB is real, useful, and partially state-aware, but it is still a projection layer with missing views and no explicit routing mandate. For token-cost reduction, the best path is a combination:

- DB-first routing for supported queries,
- new current-state and residue views,
- and continued use of docs/textbook as the long-form canonical narrative layer.

The prior audit should be treated as a document-surface audit, not as evidence that the DB layer does not exist.
