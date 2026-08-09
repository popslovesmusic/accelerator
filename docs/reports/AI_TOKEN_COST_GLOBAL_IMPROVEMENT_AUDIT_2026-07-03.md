# Global AI Token Cost Reduction Audit

Date: 2026-07-03
Mode: manual repository audit only
Scope: docs, textbook, governance reports, and adjacent generated-output surfaces that are likely to be loaded into AI context
Constraint: no validator was run as part of this audit; current repository health remains pass per `outputs/audits/global_health_report.json`

## Executive Summary

The repository is structurally strong, but it is prompt-expensive. The main token-cost drivers are:

- a very large textbook file that is likely to be loaded as context too often
- a high count of Markdown files under `docs/`
- repeated report and governance boilerplate across many documentation surfaces
- a very large generated-output tree that is useful as evidence but expensive as context

There is already a compression intent in the repository, especially in `docs/governance/operational_memory_compression.md` and the DB/index layers. The gap is that compression is advisory, not the default reading path. The best improvement is to make short canonical summaries and index manifests the primary AI entrypoints, with long-form material loaded only on demand.

Overall assessment:

- Token efficiency: partial
- Retrieval cost: high
- Duplication cost: high
- Compression governance: present, but weakly enforced
- Current global validation state: pass

## Method

Manual inspection only. I reviewed:

- `docs/AGENTS.md`
- `docs/textbook/mono_process_textbook_complete.md`
- `docs/governance/operational_memory_compression.md`
- `docs/governance/GLOBAL_VALIDATION_ROUTINE.md`
- `docs/external_program_audit_2026_07_02.md`
- `docs/external_program_audit_2026_06_28.md`
- `outputs/audits/global_health_report.json`

I also measured key doc and output counts to estimate prompt-cost pressure.

Current evidence vs historical residue:

- Current evidence: live docs, current textbook, current health report, current governance guidance
- Historical residue: older external audits and legacy reports, useful for lineage but not current authority

## Quantitative Signals

| Metric | Observed value | Token-cost implication |
|---|---:|---|
| Markdown files under `docs/` | 692 | High navigation and retrieval overhead |
| `docs/textbook/mono_process_textbook_complete.md` | 282,987 bytes / 2,391 lines | Monolithic context sink |
| Files under `docs/reports/` | 17 | Small enough to standardize aggressively |
| Files under `docs/governance/` | 42 | Governance prose is spread across multiple entrypoints |
| Files under `outputs/` | 13,730 | Large generated surface; expensive if loaded directly |
| Total bytes under `outputs/` | 767,203,621 | Strong reason to index, summarize, and archive by default |

## Findings

### 1. The textbook is the largest single prompt-cost source

Severity: high

`docs/textbook/mono_process_textbook_complete.md` is the dominant text surface. At 2,391 lines, it is too large to be a routine first-read artifact for most AI tasks.

Why this matters:

- Every routine task that loads the textbook pays a large fixed token cost.
- Most tasks only need a small current-state capsule, not the full canonical narrative.
- Long reference material encourages the model to spend context on historical detail instead of current work.

### 2. The docs tree is broad enough to justify a summary-first index

Severity: high

The repository contains 692 Markdown files under `docs/`. That is a healthy documentation ecosystem, but it is too broad to navigate ad hoc in a token-efficient way.

Why this matters:

- AI retrieval becomes expensive when the assistant has to sample many files to reconstruct current state.
- The cost is not just size; it is also branching. More files means more opportunities to load duplicate or stale material.

### 3. Generated outputs are useful evidence but costly as context

Severity: high

The `outputs/` tree contains 13,730 files and over 767 MB of data. This is appropriate for traceability, but it is not efficient as default AI context.

Why this matters:

- Asking an AI to infer "current state" from raw outputs will waste tokens.
- The repository needs shallow indices and summary manifests so agents can avoid reading raw generated artifacts unless necessary.

### 4. Compression exists as a concept, but not as a default reading protocol

Severity: medium

`docs/governance/operational_memory_compression.md` already states the intent to compress long-horizon operational history into stable oversight summaries. That is the right direction, but the repo does not yet enforce a summary-first retrieval policy everywhere.

Why this matters:

- The repository already knows it should compress.
- The remaining work is to operationalize that intent so agents start from the smallest trustworthy capsule.

### 5. Report and governance prose still repeat across many files

Severity: medium

The docs corpus contains multiple report families and governance notes with similar boilerplate. This is normal for a growing program, but it is a prompt-cost multiplier.

Why this matters:

- Repeated methodology text, repeated caution language, and repeated status phrasing all consume tokens without adding much new signal.
- Shared templates or include-based patterns would reduce drift and context size.

## Recommended Improvements

### Priority 1: Create a short current-state capsule

Create a very small, stable entrypoint in `docs/` or `docs/governance/` that answers:

- what is current
- what is historical residue
- which files are authoritative
- which file should be read next for a given task class

Expected effect: high token savings for ordinary agent tasks.

### Priority 2: Split the textbook into summary and appendices

Keep the current textbook as the long-form source of record, but add a short companion summary that is optimized for routine AI context loading.

Recommended shape:

- `current_state_summary.md`
- `current_state_index.md`
- `appendices/` for long lineage and proof detail

Expected effect: high token savings and lower accidental context loading.

### Priority 3: Standardize report headers and section order

Require a compact header for every report with:

- report purpose
- current vs historical source labels
- evidence paths
- token-cost relevance
- explicit non-claims

Expected effect: medium token savings and lower review ambiguity.

### Priority 4: Make `outputs/` index-first, not raw-first

Keep raw outputs for traceability, but expose a small manifest layer that summarizes:

- current run status
- current report pointers
- latest validations
- unresolved blockers

Expected effect: high token savings when agents ask for current status.

### Priority 5: Reduce duplicate governance boilerplate

Consolidate repeated prose into shared snippets or template fragments where possible, especially for:

- status disclaimers
- methodology sections
- historical-residue language
- report footers

Expected effect: medium token savings and lower maintenance burden.

### Priority 6: Put token budget guidance into governance

Add a short rule set that says:

- default to summary-first reading
- load appendices only when needed
- avoid raw outputs unless the task explicitly needs them
- prefer indices and manifests over full documents

Expected effect: medium token savings and less accidental over-contexting.

## Textbook Sync Check

I audited `docs/textbook/mono_process_textbook_complete.md` for stale references relevant to this audit. I did not find a token-cost-specific section that required a textbook patch, so no textbook edit was necessary for this task.

## What This Does Not Prove

- It does not measure actual model billing or inference latency.
- It does not prove that every long document should be shortened.
- It does not replace the need for raw evidence when a detailed review is required.
- It does not claim that the recommended changes are already implemented.

## Bottom Line

The repository can reduce AI token cost materially without sacrificing traceability. The biggest wins will come from making summary-first entrypoints, compact indices, and output manifests the default path, while keeping the current long-form artifacts available as deep evidence only.
