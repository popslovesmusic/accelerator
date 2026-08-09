# Acellorator: Features & Safeguards (Project Narrative)

This repository is not "one simulator"; it is a **governed research workspace** designed to run, compare, and constrain simulation-based exploration of **"THE LAW OF THE ONE PROCESS"** across multiple independent mechanism classes. The project's center of gravity is **workflow governance**: terminology control, evidence provenance, tool rigor endorsement, and claim-strength gating.

The rest of this narrative describes (1) what the project *does* (features) and (2) what it is engineered to *prevent* (safeguards).

---

## 1) What This Project Provides (Features)

### 1.1 Multi-engine ecosystem (model diversity by design)

The `tools/` directory is an ecosystem of simulation and analysis tools spanning multiple model classes and mechanism classes. A typical pattern is:

- **Python prototype tools** (readable baselines; fast iteration)
- **C++ / AVX2 / SYCL tools** (high-performance implementations; validation and provenance expectations)

The tool inventory and interfaces are centralized in:

- `registry/tool_manifest.json` (tool list, entry points, CLI templates, mechanism class, declared rigor endorsement status)
- `registry/tool_index.json` and `registry/validation_index.json` (indexing / validation metadata)

Each tool typically contains a `validation/` directory with an explicit `rigor endorsement_manifest.json` describing observables, controls, known limits, and the scientific-validity checklist (implementation verification, numerical stability, reproducibility, cross-model checks, falsification, UQ, provenance).

### 1.2 Standardized, config-driven execution (reproducible runs)

Runs are driven by JSON configs under `configs/` and write **recoverable artifacts** under `outputs/`. The repo’s tooling is organized around an assumption that:

- you create a new config for each experiment, and
- you write outputs into a new run directory, rather than overwriting defaults.

The primary orchestrator for multi-tool runs is:

- `scripts/multi_sim_runner.py` (config-driven orchestration, seed handling, aggregation, and governance packet emission)

The high-level “one entry point” wrapper described in the user docs is:

- `oneproc/` (a governed CLI wrapper; notably distributed here as compiled Python bytecode rather than `.py` sources)

### 1.3 A registry-first “research OS” layer

`registry/` functions as the project’s **operational control plane**. Key roles include:

- **Compliance and translation authority:** `registry/compliance_charter_v2_3.json`
- **Lexicon system:** canonical terms, alias normalization, gap queue, and validation registry
  - `registry/lexicon_canonical.json`
  - `registry/lexicon_alias_map.json`
  - `registry/lexicon_gap_queue.json`
  - `registry/lexicon_validation_registry.json`
- **Evidence/claim indexing:** `registry/evidence_index.json`, `registry/claim_registry.json`
- **Validation governance:** `registry/validation_protocol_v2.json`, `registry/falsification_standard_v1_0.json`, `registry/cross_verification_protocol.json`
- **Writing templates:** `registry/writer_templates.json`

In practice, the “research system” lives in these registries plus the gate/orchestration scripts, not in any single engine.

### 1.4 Paper-like outputs and publication scaffolding

The repo contains a growing set of governed paper-style reports under:

- `docs/reports/papers/`
- `zenodo/` (publication packaging directory)

The writing norm is explicit: conclusions are scoped to the model world (see Safeguards below).

---

## 2) What This Project Enforces (Safeguards)

The project’s safeguards are designed to reduce two failure modes:

1) **Overreach** (treating a model observation as universal truth), and  
2) **Single-mechanism lock-in** (treating one update rule as “the theory”).

### 2.1 “Mechanism independence > tool count”

A core governance principle is that confidence comes from **independent mechanism classes**, not from repeatedly running one engine. This is operationalized in `registry/validation_protocol_v2.json` via minimum mechanism counts and independent-measurement requirements.

Related artifact:

- `registry/cross_verification_protocol.json` (how to define observables, run multiple tool classes, normalize outputs, compare agreement, and require falsification for “supported” outcomes)

### 2.2 Lexicon compliance and term gating (preventing undefined vocabulary)

This repo treats terminology as a governed system, not an informal glossary:

- **Alias normalization** maps surface forms to canonical terms.
- **Validation-by-role** constrains how strongly any term can be used in claims.
- **Gap capture** forces new/unstable terms into `lexicon_gap_queue.json` rather than silently inventing vocabulary in a paper.

The enforcement path is implemented in:

- `scripts/governance_gate.py` (includes lexicon in-checks and validation checks; can auto-generate lexicon gap/registry patches when lexicon checks fail)
- `scripts/lexicon_governor.py` and `scripts/lexicon_resolve.py` (lexicon audit/normalization helpers)

Practical effect: if a paper/claim uses terms whose roles are below required validation levels, the best-allowed classification is downgraded (e.g., capped at “proposed interpretation”).

### 2.3 Claim gates (automatic downgrade/block instead of persuasion)

The repo’s governance is designed so that “paper polish” cannot compensate for missing evidence. The gate stack described in `registry/validation_protocol_v2.json` includes:

- template structure checks (required sections, non-empty constraints, and mandated conclusion prefix)
- metadata/body consistency checks
- lexicon validation checks
- measurement requirements (including independent measurement for C4+ claims)
- falsification requirements
- C++ preference checks for higher-rigor runs
- language-policy checks (terminology and prohibited primitives, per charter)

The gate implementation lives in:

- `scripts/governance_gate.py`

And the falsification requirement is specified in:

- `registry/falsification_standard_v1_0.json` (four-vector falsification standard, FV-1..FV-4)

Practical effect: high-level claim strength is not “negotiated”; it is **computed** from tool rigor endorsement, evidence artifacts, and governance rules.

### 2.4 Tool rigor endorsement manifests (explicit scientific-validity checklist)

Each tool’s `validation/rigor endorsement_manifest.json` is a compact “safety contract” for research use. It typically records:

- declared rigor endorsement level (C0–C4)
- validated observables
- known controls and known limits
- required metadata fields (seed, config hash, backend, precision, timestamp, source commit)
- the scientific-validity checklist booleans (implementation verified, numerical stability, reproducibility, cross-model validated, falsification verified, uncertainty quantified, provenance verified)

Practical effect: tool readiness constrains what the project considers an allowable claim, and it forces explicit acknowledgement of limits.

### 2.5 Provenance and “ground zero” reset rules

The compliance charter explicitly frames data provenance as non-negotiable, including a “ground zero” declaration about unrecoverable prior simulation data. The intended safeguard is:

- no empirical statement is allowed to stand without a **recoverable source file** produced under the charter’s current rules.

Primary authority:

- `registry/compliance_charter_v2_3.json`

Supporting indices:

- `registry/evidence_index.json`
- `outputs/` (run artifacts)

### 2.6 Humility constraint (scope guardrail)

The writing standard is deliberately scoped: conclusions are required to begin with:

> "Within these models..."

This is repeatedly reinforced in onboarding docs and is also treated as a template gate requirement for high-rigor work.

---

## 3) How to Read the Repo (Practical “map”)

If your goal is to understand capabilities and constraints quickly:

1) Start with `README.md` and `ONBOARDING.md` for the intent and workflow posture.  
2) Skim `docs/reports/TOOL_SCIENTIFIC_RIGOR_REPORT_2026-04-30.md` to see which tools are considered claim-ready and why.  
3) Open `registry/tool_manifest.json` to see the actual execution interface and declared mechanism classes.  
4) Open `scripts/governance_gate.py` to see which checks are enforced at validation time.  
5) Inspect a tool’s `validation/rigor endorsement_manifest.json` to see its current scientific-validity posture and known limits.  

---

## 4) What This Narrative Does *Not* Claim

This document describes **repository features and safeguards**. It does not claim that any specific theoretical statement is true in the world, nor that any particular result is established; those require recoverable outputs and a governance pass under the current charter.
