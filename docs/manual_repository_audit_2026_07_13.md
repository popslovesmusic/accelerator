# Manual Repository Audit: Staleness, Redundancy, Blockers, Debt, Obligations, and Improvements

**Audit date:** 2026-07-13  
**Mode:** Manual repository audit outside governance classification  
**Scope:** Tracked repository structure, executable validation paths, tests, dependencies, documentation, generated artifacts, current obligations, and textbook synchronization  
**Local governance found and applied:** Yes, `GEMINI.md` was read. It constrained claim language and reporting structure but was not used as the source of audit findings.  
**Mutation boundary:** This report is the only audit-authored repository change. Existing working-tree changes were not modified.

## Evidence Classification

The labels below describe repository-audit evidence, not framework claim promotion:

- **C0:** Unverified indication or review hypothesis.
- **C1:** Direct static observation in one repository surface.
- **C2:** Corroborated static observation across multiple repository surfaces.
- **C3:** Reproduced executable behavior or command result.
- **C4-C5:** Not assigned by this audit; no independent external replication was performed.

## 1. Scope

This audit looked for:

- stale or conflicting documentation;
- exact and functional redundancy;
- execution and validation blockers;
- technical and repository debt;
- open obligations recorded in project surfaces;
- improvements that reduce false confidence, maintenance cost, and audit latency.

The audit did not change governance records, registries, claims, mathematical objects, simulation outputs, or engine code. It did not assess the external truth of the Mono-Process Framework.

The working tree was already dirty at audit start. Pre-existing modifications were present in:

- `governance/live/program_task_registry.json`
- `outputs/audits/global_health_report.json`
- `registry/db/README.md`
- `scripts/db/db_health_check.py`
- `scripts/db/db_maintenance.py`

## 2. Directly Observed / Defined

### Executive Ruling

**Operational ruling: blocked for a trustworthy full-validation claim; usable for bounded manual work.** [C3]

The latest global report says `overall_status: pass`, but the ordinary pytest suite does not collect successfully, the engine stage tests zero tools, warning stages are normalized into the overall pass, and two stages named as part of the full plan are skipped. The current green status therefore does not establish that the repository's executable surface is healthy. [C3]

### Priority Findings

| ID | Priority | Category | Finding | Evidence | Impact |
|---|---|---|---|---|---|
| F-01 | P0 | Blocker / validation | The global validator can report an overall pass despite warning stages, zero-work stages, and skipped stages. | `scripts/global_validate.py` treats `warning` and `skipped` as terminal pass states. The final 2026-07-13 report contains 128 hygiene warnings, 3 math-program warnings, 34 governance-integrity warnings, zero tested engines, and skipped DB-runtime and patch-chain stages. [C3] | "Green" is not a reliable release or promotion gate. |
| F-02 | P0 | Blocker / tests | The test suite fails during collection. | `python -m pytest --collect-only -p no:cacheprovider` collected 50 tests and failed in three modules. `typer` is unavailable in the active interpreter; two tests import tool modules that are not on the import path. [C3] | There is no clean baseline from which regressions can be distinguished. |
| F-03 | P0 | Blocker / evidence | At least one validator grants passes from file existence while substantive checks remain TODOs. | `scripts/validate_msv_001_run.py` sets config, falsification, and provenance passes without schema, vector-content, or required-field validation. [C2] | Malformed or incomplete evidence can be classified as eligible. |
| F-04 | P0 | Blocker / evidence | A campaign script contains synthetic measurements and mocked falsification passes while producing high-rigor metadata and paper language. | `scripts/run_10_t003_web_ensemble.py` constructs spectral values arithmetically and labels four falsification vectors passed without executing them. [C1] | Accidental execution could generate artifacts that resemble real evidence. |
| F-05 | P1 | Staleness / claims | The foundational narrative conflicts with the active humility language. | `MATH_PROGRAM_NARRATIVE.md` says a simulation result "proves" invariance, calls the grammar "universal," and describes "formal proof of the four foundational laws of reality." [C2] | Public-facing interpretation can exceed the repository's stated evidence limits. |
| F-06 | P1 | Staleness / encoding | Canonical and orientation-facing documents contain mojibake. | `GEMINI.md` corrupts the core expression and the C0-C5 range. Mojibake was also detected in `reports/triage_report_2026-05-08.md` and one theory report. [C2] | The canonical expression can be copied or parsed incorrectly. |
| F-07 | P1 | Repository debt | Generated evidence and local environments dominate tracked content. | Of 36,878 tracked files, 13,790 are under `outputs/`, 11,803 under `results/`, 406 under `validation/results/`, and 862 under `gpt_folder_bridge/.venv/`. The Git pack is 4.10 GiB. [C3] | Clone, search, diff, backup, and audit operations are costly and time out. |
| F-08 | P1 | Hygiene | The root contains tracked binaries, build products, test outputs, and historical audit JSONs despite ignore rules for several of those classes. | Tracked examples include `.obj`, `.pyd`, `.lib`, `.exp`, test result JSON/CSV, and multiple `final_audit*.json` files. [C2] | Source and generated state are mixed; cleanup policy is not retroactive. |
| F-09 | P1 | Test debt | Automated test density is low relative to the Python surface. | The repository tracks 1,924 Python files and 13 files under `tests/`; pytest discovered 50 tests before collection failed. [C2] | Large validator and orchestration surfaces lack a proportionate regression net. |
| F-10 | P1 | Error handling | Broad exception suppression is widespread. | Static search found 77 bare `except:` occurrences across Python under `scripts`, `tools`, `engines`, and `tests`. `scripts/aggregate_results.py` silently drops malformed inputs in every aggregation branch. [C2] | Missing or corrupt evidence can disappear without a diagnostic or failed run. |
| F-11 | P1 | Obligations | The formal-system closure obligations remain open. | `docs/textbook/textbook_formal_system_gap_assessment.md` records missing syntax, semantics, truth conditions, inference rules, operator algebra, model class, and failure conditions. The textbook still records deferred termination, confluence, proof, and bridge-rigor work. [C2] | Formal-proof and closed-calculus language remains ahead of the documented formal system. |
| F-12 | P1 | Obligations | Economics-specific work remains blocked even though global summaries can appear healthy. | `outputs/audits/economics_health_report.json` records E3 as next target, E4-E7 blocked, five open debts, and three validation-blocking debts. [C2] | Economics projection or policy promotion is not currently supportable. |
| F-13 | P2 | Redundancy | A vendored C++ JSON header is copied exactly across 14 tool directories, with a fifteenth distinct copy in the PDE engine. | Fourteen `json.hpp` files share Git blob `ceb7a9f...`; the PDE copy has a different blob. [C2] | Security/version updates require many synchronized edits and can drift. |
| F-14 | P2 | Redundancy / staleness | Eleven mathematical schema versions remain side by side without a clear current-version pointer in their directory. | `docs/MONO_PROCESS_MATHEMATICAL_SCHEMA_V1.md` through `V2_2.md` are present; V1_7 and V2_0 are absent. [C1] | Reviewers can select an obsolete schema or infer a nonexistent linear version history. |
| F-15 | P2 | Portability | The textbook contains absolute `file:///D:/projects/acellorator/...` links. | Seven matches were found in `docs/textbook/mono_process_textbook_complete.md`. [C1] | Links fail outside this workstation and in normal repository renderers. |
| F-16 | P2 | Audit redundancy | Several recent manual audits overlap in subject and conclusions without a single audit index or supersession marker. | `docs/external_program_audit_2026_06_28.md`, `_07_02.md`, and `_07_05.md` coexist with similar scope. [C1] | Readers must manually determine which audit is current and which findings remain open. |
| F-17 | P2 | Dependency reproducibility | Dependency declarations do not establish a reproducible active environment. | `requirements.txt` is unpinned; `requirements.lock.txt` is pinned, but the active interpreter reports pytest 9.1.1 instead of locked 9.0.3 and cannot import locked dependency `typer`. There is no root `pyproject.toml`. [C3] | Test behavior depends on invocation environment and manual path setup. |
| F-18 | P2 | Hygiene validator | The results naming rule and its warning text are semantically confusing. | `HygieneValidator` calls `YYYY-MM-DD_runNN_name` a legacy format, while `TODO.md` says legacy results should be standardized to that same schema. [C2] | A remediation task can increase warnings or remain impossible to close unambiguously. |
| F-19 | P2 | Report freshness | The latest full validation still emits `STALE_REPORT_WARNING` immediately after rewriting the report. | `outputs/audits/global_health_report.json` records `stale_report_warning: true` and an overall pass. [C3] | Report freshness is not a clear postcondition and can become permanent noise. |
| F-20 | P2 | Documentation debt | `TODO.md` is mostly a historical completion ledger rather than a compact active backlog. | Most of the file consists of completed tasks; active items are mixed into the same long document. [C1] | Current obligations are difficult to scan and easy to contradict elsewhere. |

### Test Collection Blockers

The three collection errors are directly actionable: [C3]

1. `tests/test_lexicon_cli.py`: `ModuleNotFoundError: No module named 'typer'`.
2. `tests/test_rd_boundary_scaling_policy.py`: `ModuleNotFoundError: No module named 'rd_moving_boundary_sim_v1'`.
3. `tests/test_tda_adjacency_threshold.py`: `ModuleNotFoundError: No module named 'tda_module_v1'`.

The latter two tests import tool directories as top-level packages but the repository has no root packaging configuration that installs or maps them. This is a test-environment design problem, not evidence that the tested implementations themselves fail. [C2]

### Validation Status Mismatch

The latest full report records the following bounded facts: [C3]

- runtime: 28.52 seconds;
- `overall_status`: `pass`;
- hygiene: `warning`, 128 warnings;
- math program: `warning`, 3 warnings;
- governance integrity: 34 warnings;
- engine tools tested: 0;
- DB runtime: skipped by mode;
- patch chain: skipped by mode;
- stale report warning: true.

The validator's final reduction treats `success`, `warning`, `pass`, and `skipped` as acceptable terminal states. This explains the mismatch; it is not merely a report-format issue. [C3]

### Repository Composition

Tracked file counts observed during the audit: [C3]

| Surface | Tracked files |
|---|---:|
| Entire repository | 36,878 |
| JSON | 22,017 |
| Logs | 6,548 |
| CSV | 2,167 |
| Python | 1,924 |
| PNG | 1,514 |
| Markdown | 1,104 |
| Binary `.bin` | 771 |
| `outputs/` | 13,790 |
| `results/` | 11,803 |
| Embedded `.venv/` | 862 |

The largest tracked blob is a 46.3 MB benchmark snapshot. Other large tracked files include runtime DLLs, smoke-run CSVs, long JSONL traces, and generated NPZ snapshots. The Git object database is 4.10 GiB. [C3]

## 3. Inferred Inside Framework

- The dominant maintenance problem is source-of-truth and evidence-boundary control, not validator runtime. The final audit validation completed in about 29 seconds, but its pass semantics are too permissive to establish broad health. [C3]
- The repository is carrying archival data, recoverable evidence, local build products, source, and current operational state in one Git history. Without an explicit retention and release model, each new campaign increases audit latency and ambiguity. [C2]
- Formal and empirical claim language has evolved faster than older orientation documents were retired or rewritten. The textbook is more cautious than `MATH_PROGRAM_NARRATIVE.md`, leaving two conflicting reviewer entry points. [C2]
- Existing governance summaries can report zero global debt while subsystem SSOTs still report open blocking debt. A non-governance reviewer therefore needs a consolidated cross-subsystem obligation index. [C2]
- Repeated audit documents and completed roadmap entries are functioning as an append-only historical record without explicit supersession metadata. This preserves history but weakens operational clarity. [C2]

## 4. External Resemblance (Analogy Only)

The repository resembles a monorepo that also serves as a data lake, archival deposit, publication bundle, governance ledger, and active application workspace. That structure can preserve provenance, but it requires stronger boundaries than a source-oriented repository because ordinary source-control signals no longer distinguish executable code from generated evidence. [C1]

The validation design resembles a dashboard aggregator more than a strict release gate: it records many subsystems, but warnings, skips, and zero-work results do not prevent a green summary. This is a structural analogy only. [C2]

## 5. What It Does Not Prove

- This audit does not prove that any mathematical or scientific claim is true or false.
- It does not prove that the 50 collected tests would fail after environment repair.
- It does not establish that every bare exception is defective; some are cleanup or fallback paths.
- It does not establish that all tracked outputs are unnecessary; many may be required evidence artifacts.
- It does not establish that every historical schema or audit should be deleted; archival retention may be intentional.
- It does not replace governance authority, claim gates, registries, or formal review.

## 6. Failure Modes / Uncertainty

- The audit used the current working tree, which contains uncommitted changes. Findings tied to the latest health report and DB validator may differ from `HEAD`. [C1]
- Exact repository-wide duplicate analysis timed out because of repository volume. The duplicated JSON header result was confirmed from Git blob hashes, but no claim is made that it is the largest duplicate family. [C3]
- File timestamps are workstation timestamps and were used only as orientation, not as authoritative publication dates. [C1]
- Pytest collection used the active system Python, not a verified lockfile environment. This is itself a reproducibility finding, but it limits conclusions about test implementation health. [C3]
- The audit did not execute simulations or modify generated evidence. [C1]

## Obligations Register

These are the clearest outstanding obligations visible outside governance runtime classification:

| Obligation | Source | Current state | Dependency / blocker | Evidence |
|---|---|---|---|---|
| Repair test collection and define the supported test environment | pytest collection, requirements files | Blocked | Missing dependency installation and package-path strategy | C3 |
| Make full validation fail or become explicitly degraded on warnings, skips, and zero-work critical stages | global validator and latest report | Open | Pass-policy redesign and stage criticality declaration | C3 |
| Replace placeholder MSV validation with content validation | `scripts/validate_msv_001_run.py` | Open | Schemas and required field/vector definitions | C2 |
| Quarantine or remove mock evidence-generation behavior | `scripts/run_10_t003_web_ensemble.py` | Open | Historical artifact review | C1 |
| Close formal-system gaps before using closed-calculus language | formal-system gap assessment | Open | Grammar, semantics, inference, model, countermodel, failure rules | C2 |
| Resolve economics E3, then E4-E7 | economics SSOT and health report | Blocked | E3 Sigma_D distinguishability | C2 |
| Resolve active TODO items 7.1-7.4 and 8.1-8.3 | `TODO.md` | Open | Formal definitions, lexicon closure, result naming policy, SSOT formalization | C1 |
| Replace workstation-absolute textbook links | textbook | Open | Relative-link normalization | C1 |
| Establish generated-artifact retention and archive policy | Git tree and `.gitignore` | Open | Decide what must remain in Git versus archival bundles | C2 |
| Add audit/schema supersession indexes | docs | Open | Canonical-current pointers and archive metadata | C1 |

## Recommended Improvement Sequence

### Phase 1: Restore Trustworthy Gates

1. Fix pytest collection using one supported environment command and explicit package installation/path configuration.
2. Add a validator policy that distinguishes `PASS`, `PASS_WITH_WARNINGS`, `DEGRADED`, `SKIPPED_NONCRITICAL`, `SKIPPED_CRITICAL`, and `FAIL`.
3. Require nonzero checked-item counts for critical stages unless an explicit empty-scope declaration is emitted.
4. Include DB-runtime and patch-chain checks in the definition of full validation, or rename the current mode to avoid claiming full coverage.
5. Add regression tests for warning aggregation, skipped critical stages, zero-tool engine validation, and stale-report behavior.

### Phase 2: Close Evidence-Safety Gaps

1. Implement actual JSON Schema checks and required-field validation in `validate_msv_001_run.py`.
2. Make falsification checks validate named vectors, execution records, outcomes, and provenance rather than file presence.
3. Move mock campaign scripts under an explicitly non-evidence fixture/example surface, or make them terminate unless a test-only flag is supplied.
4. Replace bare exception suppression in evidence aggregation with typed exceptions, source-path diagnostics, and failed/partial aggregation status.

### Phase 3: Reduce Repository Weight

1. Define retention classes: source, canonical small evidence, reproducibility manifest, publication bundle, and external archive.
2. Stop tracking embedded virtual environments and root build products.
3. Move bulky recoverable outputs to versioned archival bundles or object storage while retaining checksums and manifests in Git.
4. Remove already-tracked ignored artifacts only through a reviewed migration that preserves required evidence references.
5. Measure repository size and audit duration before and after migration.

### Phase 4: Consolidate Documentation

1. Make one reviewer-start document canonical and mark older narratives as superseded or historical.
2. Rewrite unsupported claim-escalation language and repair canonical-expression mojibake.
3. Add `docs/audits/INDEX.md` with current, superseded, and open-finding status.
4. Add a schema index naming the current schema and explaining missing/nonlinear version numbers.
5. Replace absolute textbook links with repository-relative links.
6. Split `TODO.md` into a compact active backlog and an archived completion ledger.

### Phase 5: Improve Dependency and Test Architecture

1. Add a root packaging/test configuration, preferably `pyproject.toml`, with explicit test paths and tool package mapping.
2. Make the lockfile installation command canonical and verify it in CI.
3. Expand tests around validators, evidence parsers, aggregators, and report status reduction before adding broad simulation tests.
4. Add static checks for bare exceptions, TODO-based pass paths, mock evidence markers, absolute local links, and mojibake.

## Textbook Synchronization Audit

The textbook was checked as required. No textbook patch was made because this task was an independent audit and did not authorize changes to the mathematical or governance narrative. The following mismatches remain: [C2]

- the textbook records multiple pending formal, bridge, and proof obligations while older narrative surfaces use stronger closure language;
- seven absolute workstation links remain;
- sections around orientation metrics preserve older pending-build language alongside later pending-rigor language, making chronology difficult to interpret without source-patch context;
- the textbook says expansion remains frozen while a governance-only closure task is active, but this audit intentionally did not resolve that authority question outside governance.

**Textbook synchronization status: reviewed, mismatch reported, not patched.** [C2]

## Command Evidence

Primary read-only commands used:

```text
git status -sb
git ls-files
git ls-tree -r -l HEAD
git count-objects -vH
rg --files
rg -n <targeted patterns>
python -m pytest --collect-only -p no:cacheprovider
```

The final global report used as evidence was `outputs/audits/global_health_report.json`, run ID `GV-20260713T072526.896883-12704`, with recorded duration 28.523246 seconds. [C1]

## Final Disposition

- **Staleness:** Material; claim language, encoding, links, roadmap presentation, and overlapping status surfaces need consolidation. [C2]
- **Redundancy:** Material; generated data, embedded environment files, copied dependencies, schema versions, and audits add maintenance cost. [C2]
- **Blockers:** Test collection, permissive full-validation semantics, placeholder validators, and mock evidence paths are immediate blockers to a trustworthy global-health claim. [C3]
- **Debt:** High repository and validation debt; runtime duration itself is no longer the primary issue. [C3]
- **Obligations:** Formal-system closure, economics E3-E7, active roadmap gaps, evidence validator completion, and artifact retention policy remain open. [C2]
- **Recommended next action:** Repair the test environment and validator status semantics together, then establish a clean reproducible baseline before addressing repository-size migration. [C3]
