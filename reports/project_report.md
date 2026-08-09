# Acellorator Project Process Report

Date: 2026-05-03  
Scope: project process + governance workflow audit (manifests/registry/scripts).  
Non-scope: modifying any simulation engine logic (especially C++ tools).

## Executive Summary

- **Registry alignment is now mechanically consistent**: `registry/tool_manifest.json` matches every tool-local `tools/*/validation/certification_manifest.json`, and the tool directories are fully registered (`tools/` ↔ manifest ↔ index are all **50/50/50**).
- **C++ tools are present and operationally addressable** at the filesystem level: all 24 C++ tools listed in `registry/tool_index.json` have an existing `entry_point`, and all cert manifests parse as valid JSON.
- The primary remaining risks are **process-level** (path conventions, CLI ergonomics, and brittle scripts) rather than missing tooling.

## Current “Source of Truth” Files

- Tool registry:
  - `registry/tool_manifest.json` (tool definitions; runner-facing)
  - `registry/tool_index.json` (normalized index; governance-facing)
- Governance authorities:
  - `registry/compliance_charter_v2_3.json`
  - `registry/validation_protocol_v2.json`
- Lexicon authorities:
  - `registry/lexicon_canonical.json`
  - `registry/lexicon_alias_map.json`
  - `registry/lexicon_gap_queue.json`
  - `registry/lexicon_validation_registry.json`

## Verified Invariants (as of 2026-05-03)

- `scripts/check_tool_manifest_sync.py --manifest registry/tool_manifest.json` returns **OK**.
- `scripts/check_manifest_gaps.py` reports all `_cpp` directories are registered in `registry/tool_manifest.json`.
- Directory/index/manifest agreement:
  - `tools/` directories: **50**
  - manifest tools: **50**
  - index tools: **50**
- C++ operational artifacts:
  - all C++ `entry_point` paths exist (filesystem check)
  - all `tools/*/validation/certification_manifest.json` parse as valid JSON

## Process Errors / Fragilities Found

### 1) `scripts/governance_gate.py` is not CLI-safe

- It does not implement `--help` / argparse; passing `--help` is treated as a paper path and triggers `FileNotFoundError`.
- It emits a Python 3.14 deprecation warning (`datetime.utcnow()`), which will eventually become a hard failure.

Impact:
- Governance gate is “correct-by-convention” but not “operator-proof”; accidental misuse is easy.

Recommendation:
- Wrap the existing positional-arg behavior with `argparse` (retain backwards compatibility), and replace `utcnow()` with timezone-aware UTC timestamps.

### 2) `scripts/lexicon_resolve.py` appears out-of-date with current repo layout

Observed:
- Repo root discovery depends on a root-level `tool_manifest.json` (current canonical is `registry/tool_manifest.json`).
- Alias map is loaded from `theory/lexicon/lexicon_alias_map.json` (current canonical is `registry/lexicon_alias_map.json`).
- Token regex includes garbled encoded epsilon/rho sequences, suggesting an encoding/copy issue.

Impact:
- Any workflow depending on `lexicon_resolve.py` will likely fail or silently produce incomplete mappings.

Recommendation:
- Align `lexicon_resolve.py` to `registry/*` paths and use the existing path-mapping conventions (`registry/path_mapping.json`) if intended.

### 3) `scripts/init_workspace.py` can create structurally-invalid registries

Observed:
- It creates missing registry JSON files as empty `{}`. Several consumers expect structured JSON (e.g., `tool_manifest.json` expects `{ project, version, tools: [...] }`).

Impact:
- Fresh workspace initialization can create a broken governance state that fails later, far from the source of the problem.

Recommendation:
- Emit schema-correct skeletons for each required registry file, or refuse to create the file unless a template exists.

### 4) Cert/manifest tooling risks string-order bugs

Observed:
- `scripts/finalize_certification.py` uses comparisons like `cert_level >= "C2"` which are lexicographic string compares.

Impact:
- Can misclassify certification tiers if formats evolve (e.g., `C10`).

Recommendation:
- Parse `C<number>` to an integer for comparisons.

### 5) `scripts/multi_sim_runner.py` contains “broad except” blocks

Observed:
- Multiple `except:` without logging the exception type/message.

Impact:
- Failures can be masked and later interpreted as model behavior rather than process failure.

Recommendation:
- Replace with `except Exception as e:` and record into the run’s `preflight_report.json` or job log.

## Optimization Opportunities (Process / Reliability / Rigor)

### A) Make “tool readiness” a first-class preflight

You already have:
- `validation_path` + `certification_manifest.json`
- `scripts/check_tool_manifest_sync.py`

Opportunity:
- Add a lightweight preflight command (or `multi_sim_runner` option) that verifies:
  - entry points exist
  - cert manifests parse
  - tool cert level meets a requested run intent level
  - warns when python tool is selected and a C++ counterpart exists (CPP preference policy)

### B) Centralize path conventions

Current situation:
- Canonical manifest is `registry/tool_manifest.json`, but some scripts still assume root `tool_manifest.json` or older locations.

Opportunity:
- Define a single canonical “repo root locator” that checks `registry/tool_manifest.json` first.
- Use `registry/path_mapping.json` to preserve legacy references without breaking older configs.

### C) Improve operator ergonomics for governance gate

Opportunity:
- Add `--paper`, `--target-level`, `--intent`, `--strict` flags while preserving positional args.
- Emit a short human-readable summary line in addition to JSON.

### D) Reduce “certification drift” between local manifests and registry

You already have the correct mechanism:
- Tool-local `certification_manifest.json` is the real certification record.

Opportunity:
- Treat `registry/tool_manifest.json` and `registry/tool_index.json` as *derived caches*:
  - regenerate/sync on demand
  - avoid manual edits unless explicitly needed

### E) Control output growth and accidental repo pollution

Observation:
- Many runs and audits are produced under `outputs/`; this is correct for provenance but can flood working trees.

Opportunity:
- Ensure `.gitignore` has stable patterns for `outputs/runs/**`, `outputs/audits/**`, and other high-churn outputs (without deleting anything).

## Notes on “C++ Tools Immutable and Operational”

This audit treats “operational” as:
- entry point exists and is invokable by path
- validation artifacts exist and are parseable
- registry/manifest reflect tool-local certification truth

It does **not** claim:
- numerical correctness in every regime (that’s per-tool validation)
- runtime performance or GPU correctness (requires dedicated certification artifacts)

## Recommended Next Actions (Safe Order)

1) Fix `scripts/lexicon_resolve.py` pathing and encoding (pure process fix).
2) Add argparse support + UTC timestamp fix in `scripts/governance_gate.py` (pure UX/reliability).
3) Update `scripts/init_workspace.py` to write schema-correct skeleton registries.
4) Normalize certification comparisons in `scripts/finalize_certification.py` (`C<number>` parsing).
5) Replace broad `except:` in `scripts/multi_sim_runner.py` with logged exceptions.

