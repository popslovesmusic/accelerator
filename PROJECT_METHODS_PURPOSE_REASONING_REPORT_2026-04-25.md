# Project Methods, Purpose, and Reasoning (2026-04-25)

## 0. Scope and Purpose

This repository (“Acellorator Research Ecosystem”) is a multi-engine simulation + analysis workspace used to test **operational, falsifiable** interpretations of claims stated in `theory/THE LAW OF THE ONE PROCESS.txt`.

The project goal is not metaphysical validation. It is:

- Translate theory language into **measurable observables**.
- Execute **multi-model** simulations (different model classes).
- Apply **cross-verification + falsification** to reduce self-confirmation.
- Produce governed technical papers whose conclusions are explicitly scoped: **“Within these models…”**.

## 1. Governance and Compliance

Two layers of governance are enforced:

1) **Research governance (cross-verification + falsification)** in `AGENTS.md`.
2) **Compliance + translation + provenance governance** in `theory/lexicon/compliance_charter_v2_3.json`.

### 1.1 Claim Humility

All “support” language is defined as *model-consistency* under specified runs and observables, not universal truth.

### 1.2 Claim Classification (Charter v2.3)

The compliance charter defines how claims may be written:

- `verified` (charter sense): requires recoverable files and (where applicable) compliance with the charter’s metric schema requirements.
- `theoretical`: derivable without simulation.
- `provisional`: plausible but not yet verified under charter rules.
- `prior_finding`: supported only by unrecoverable/lost data; must be tagged and treated as hypothesis pending rerun.

Practical implication: **operational L-levels (L0–L3)** in `lexicon_validation_registry.json` are tracked, but the charter-facing classification is recorded separately to prevent overstating empirical status.

## 2. Method: Translate Theory → Primitives → Models → Observables

### 2.1 Primitive Mapping

The working primitive map (per `AGENTS.md`) is:

- `epsilon` (ε): mismatch / driver signal
- `residue` (R): accumulated constraint / memory-like state
- `coupling` (K / CSI): interaction reach

### 2.2 Multi-Model Requirement

Claims are evaluated across at least two model classes (examples from `tool_manifest.json` / repo README):

- CA (cellular automata admissibility): `ca_admissibility_sim_v1`
- FSA (rule-engine admissibility): `fsa_rule_engine_sim_v1`
- Agent-based swarm dynamics: `agent_based_sim_v1`
- Kuramoto oscillators: `kuramoto_sim_v1`
- PDE identity/box scaffold: `structural_box_sim_v2`

### 2.3 Observable Design

The pipeline uses operational observables that can be extracted directly from run artifacts, typically from `summary.json` and/or `metrics.csv` outputs:

- activity/admissibility: `active_fraction`, `active_count`
- coherence/synchrony: `order_parameter`, `local_coherence_mean`
- mismatch/residue: `mismatch_mean`, `mean_residue`, `residue_mean`

These observables are chosen because:

- They are directly measured by the tool outputs (minimizes interpretive degrees of freedom).
- They have monotonic expectations under limiting-case falsifications.

## 3. Verification Method: Cross-Model Comparison

Cross-model comparison is treated as a structured test:

- Normalize comparables to a common scale when possible (often `[0,1]` fractions).
- Compare the **directional effect** of parameter sweeps (e.g., stronger gating → reduced activity).
- Compute correlations on sweep curves when a shared axis exists.

Example (recoverable artifacts):

- Admissibility sweep comparison: `outputs/research_residue_necessity_2026-04-25/analysis/cross_model_comparison.json`

## 4. Falsification Method: Negative Controls + Limit Cases

Falsification is required when classifying a claim as “Supported” under the research governance rules.

The falsification harness is `falsification_suite_v1/run_falsification.py`, driven by suite JSON files. It asserts expected behavior in limit cases such as:

- no coupling → low synchrony (Kuramoto)
- no mismatch → inert behavior (CA)

Recoverable artifacts (examples):

- Admissibility-focused falsification: `outputs/research_residue_necessity_2026-04-25/runs/falsification/falsification_report.json`
- Lexicon validation falsification: `outputs/lexicon_validation_program_2026-04-25/runs/falsification/falsification_report.json`

## 5. Lexicon Validation Program (Operational, Charter-Aware)

The lexicon is treated as an operational system with testable roles:

- Canonical/alias normalization: `theory/lexicon/lexicon_canonical.json`, `theory/lexicon/lexicon_alias_map.json`
- Role-specific evidence + provenance: `lexicon_validation_registry.json`

### 5.1 Why Role-Specific Validation

Many terms in the theory are polyfunctional. This project avoids “global” term verification and instead validates **roles**, e.g.:

- `residue` as an **admissibility gate** vs `residue` as a **historical structural memory trace**

Only the tested role may be described as L3-supported, and charter classification may remain `provisional` if charter schema requirements are not satisfied.

### 5.2 Gap Closure Strategy

“Gaps” are closed by:

- Improving alias normalization for symbols/variants (e.g., ε/ρ/R/CSI → canonical terms).
- Promoting frequently-used primitives into canonical term status for consistent translation.
- Adding validation registry entries with explicit evidence paths and scope limits.

Charter-aware compliance notes were summarized here:

- `outputs/lexicon_charter_compliance_report_2026-04-25.json`

## 6. Tooling Added to Support Reproducibility

To reduce friction and increase repeatability of governed runs:

- Batch runner: `utilities/run_many.ps1`
- Run summarizer: `utilities/summarize_runs.py`
- Lexicon excerpt resolver (heuristic draft mapper): `utilities/lexicon_resolve.py`
- Falsification path resolution improvements: `falsification_suite_v1/run_falsification.py`

## 7. Reasoning Philosophy (Why This Structure)

The project’s methodology is built to minimize four failure modes:

1) **Overreach:** claiming universality from one model or one run.
2) **Translation drift:** using the same term inconsistently across tools/papers.
3) **Non-reproducibility:** lacking seeded, recoverable artifacts.
4) **Self-confirmation:** validating a claim with the same model class that generated it.

Accordingly:

- Every paper is structured into mapping → setup → observables → results → comparison → falsification → artifacts.
- Cross-model verification is mandatory for “Supported” classifications (research governance).
- Provenance and claim-classification rules are enforced (charter governance).

## 8. Current Limits and Next Steps (Project-Level)

Limits (as of 2026-04-25):

- Many simulators do not emit the charter annex_B “v2.3 metric schema”, so charter-level “verified” status may remain conservative (`provisional`) even when artifacts are recoverable and falsified.
- Some roles (e.g., “structure preservation”, “topological continuity”) need richer observables (TDA/graph metrics) than activity/coherence alone.

Next steps:

- Extend rerun outputs to comply with the charter annex_B metric schema where applicable.
- Add third-model-class triangulations for key roles (graph dynamics, stochastic thresholds, PDE regimes).
- Expand lexicon registry coverage to additional high-frequency gap terms (identity, regime, orientation) with role-by-role validation plans.

