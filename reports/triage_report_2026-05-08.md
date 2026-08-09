# Acellorator Project Triage Report (2026-05-08)

## Scope

This is a **repository health triage** of `D:\projects\acellorator` as observed on **2026-05-08 (America/New_York)**. It is not a research “paper” and makes no scientific claims.

## Snapshot

- Repo root contains the expected governance + tooling layout: `configs/`, `docs/`, `registry/`, `scripts/`, `tools/`, `outputs/`, `reports/`, `tests/`, `zenodo/`.
- Working tree is **dirty** (modified + untracked files), including changes under `registry/` and `outputs/`.
- Runtime environment (venv):
  - `Python 3.14.4`
  - `pip 26.0.1`

## Critical Blockers (must fix before governed work)

### 1) `registry/lexicon_canonical.json` is invalid JSON

- `python -m json.tool registry/lexicon_canonical.json` fails with:
  - `Expecting ',' delimiter: line 421 column 9`
- `scripts/governance_gate.py --help` fails early because the lexicon loader cannot parse the canonical lexicon.
- Local context near the error shows a missing comma / malformed object boundary around line ~421 (example: a `}` is followed by `"review_reason": ...` without a separating comma).

**Impact**
- Breaks governance tooling that loads the canonical lexicon (including the Unified Claim Gate).
- Blocks lexicon validation, term resolution, and any governed “publish/validate” pipeline.

**Immediate action**
- Restore a known-good `registry/lexicon_canonical.json` (e.g., `git restore registry/lexicon_canonical.json`) or repair the JSON and re-run `python -m json.tool` until it validates.

### 2) Test suite cannot import `oneproc.lexicon_cli`

- `pytest -q` fails during collection:
  - `ModuleNotFoundError: No module named 'oneproc.lexicon_cli'`
- The `oneproc/` directory contains subfolders and `__pycache__/`, but **no `.py` source files** (only compiled `.pyc` files).

**Impact**
- CI-style confidence checks cannot run.
- Developer workflow breaks for anyone expecting the `oneproc` Python package to be importable from source.

**Immediate action**
- Decide whether `oneproc/` is meant to be:
  1) a source package in-repo (add/restore `.py` sources and `__init__.py`), or
  2) an external installable dependency (update tests and docs to install it explicitly).

### 3) Pytest cache write is permission-blocked

- Pytest emits cache warnings indicating it cannot write to `.pytest_cache\...` (permission denied / cannot create path).
- Attempting `Get-Acl .pytest_cache` fails with `UnauthorizedAccessException`.

**Impact**
- Slower test runs and noisy output; can also mask other file permission problems.

**Immediate action**
- Short-term: run tests with cache disabled, e.g. `pytest -q -p no:cacheprovider`.
- Longer-term: fix workspace ACLs for `.pytest_cache/` (or remove it from the repo and let it be generated locally).

## High Priority Issues

### A) Repository includes build artifacts at the root

Examples: `*.obj`, `*.pyd`, `*.lib`, `*.exp`, and `dase_cli_test.exe` are present in the repo root.

**Impact**
- Repo bloat + noisy diffs; increases risk of committing platform-specific binaries.

**Action**
- Confirm whether these are intended checked-in artifacts. If not, add appropriate `.gitignore` entries and remove from version control.

### B) “State” directories overlap (`outputs/` vs `results/` vs `reports/` vs `docs/reports/`)

There are multiple top-level locations that appear report-like:
- `reports/` (papers + prior project report)
- `docs/reports/` (tool scientific rigor report mentioned in README/USAGE)
- `results/` (contains paper drafts under date-prefixed directories)

**Impact**
- Confusing provenance and discoverability; increases chance of referencing unrecoverable or ungoverned artifacts.

**Action**
- Pick one canonical location per artifact type (runs vs papers vs audits) and document it; optionally add a short index file with pointers.

## Medium Priority / Hygiene

### A) Text encoding issues in Markdown

Several docs display mojibake (e.g., emoji bullets appear as `ðŸ“‚`, quotes as `â€œ`).

**Impact**
- Readability and professionalism; potential downstream issues for tooling that expects UTF-8.

**Action**
- Normalize repository docs to UTF-8 (no BOM) and re-save affected files.

### B) Governance tooling warning: `datetime.utcnow()` deprecation

`scripts/governance_gate.py` emits a `DeprecationWarning` for `datetime.utcnow()` usage (Python 3.14+).

**Impact**
- Not blocking today, but will become future breakage risk as Python evolves.

**Action**
- Update governance scripts to timezone-aware UTC timestamps (`datetime.now(datetime.UTC)`), after lexicon JSON is repaired.

## Suggested “Path to Green” (minimal sequence)

1. Fix/restore `registry/lexicon_canonical.json` so `python -m json.tool` passes.
2. Re-run `scripts/governance_gate.py --help` to confirm lexicon loading no longer fails.
3. Decide `oneproc/` packaging strategy and make `pytest -q` pass collection.
4. Address `.pytest_cache` permissions or disable cache provider in CI/dev docs.
5. Optional: clean binary artifacts + standardize where papers/reports live.

## Commands Run (for reproducibility)

- `git status -sb`
- `.venv\\Scripts\\python.exe --version`
- `.venv\\Scripts\\python.exe -m pip -V`
- `.venv\\Scripts\\python.exe -m pytest -q`
- `.venv\\Scripts\\python.exe -m json.tool registry\\lexicon_canonical.json`
- `.venv\\Scripts\\python.exe scripts\\governance_gate.py --help`

