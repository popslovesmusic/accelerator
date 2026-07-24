# Analysis Department

This directory is the peer root for the Analysis Department.

The live local SSOT is `departments/analysis/department_ssot.md`, and the local agent rules are in `departments/analysis/AGENTS.md`.

The department is inducted as a read-only recommendation layer. It transforms governed state into ordered recommendations and does not modify authoritative registries.

## Crawl Mode

Issue the global command `crawl` to route to this department and activate the bounded recursive theory-analysis role defined in `GEMINI.md`.

This command is distinct from DB artifact indexing. `python scripts/db/index_artifacts.py` walks filesystem paths and writes the SQLite artifact projection; it is not an Analysis crawl, does not produce crawl findings, and does not satisfy the Analysis crawl reporting contract.

In crawl mode:

- read authorized registries, theory objects, experiments, results, proofs, and historical records;
- normalize sources, dependencies, assumptions, evidence, and versions;
- record theorem, lemma, concept, contradiction, proof-gap, counterexample, and campaign candidates;
- assign discovery, epistemic, and proof statuses;
- preserve blockers, duplicates, contradictions, and resumable frontiers;
- stop at the declared depth, compute, novelty, or review boundary.

Crawl outputs are candidate analysis only. They do not promote claims, execute work, close debt, or modify canonical registries. Every substantive output must cite its source artifacts, support level, blockers, and non-authorizations.
