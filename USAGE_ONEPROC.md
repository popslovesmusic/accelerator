# `oneproc` Usage Guide

`oneproc` is the Governed Agent Residence CLI Wrapper for the `acellorator` ecosystem. it provides a single, governed entry point for conducting research simulations and generating technical papers using worker agents (Codex and Gemini).

## 1. Overview
The core purpose of `oneproc` is to ensure that all research activities, claim promotions, and technical publications adhere to the project's strict governance rules, including:
- **Lexicon Compliance:** All terms must resolve to the canonical lexicon.
- **Scientific Rigor:** High-rigor claims (C4+) require independent measurements and C++ tool preference.
- **Structural Integrity:** Technical papers must follow the mandatory template.
- **Auditability:** Every action is recorded in a JSON trace log.

## 2. Installation & Setup
`oneproc` is a Python-based CLI. Ensure you have the required dependencies:

```bash
pip install typer pydantic
```

### Initializing the Environment
Before running research, initialize the workspace to ensure all registry files and output directories are present:

```bash
python -m oneproc.cli init
```
Use the `--repair` flag if you need to create missing empty registry files.

## 3. Core Commands

### A. Governed Research Run
The `run` command orchestrates the entire research lifecycle.

```bash
python -m oneproc.cli run --question "Is the process epsilon stable?" --target C4 --intent validate --strict
```

**New Flags:**
- `--dry-run`: Evaluate planned run and expected gates without executing workers.
- `--strict`: Enforce C++ preference as a block and require all four falsification vectors (FV-1..FV-4).
- `--intent`: Selects governance requirements (`explore`, `validate`, `publish`).

### B. Worker Orchestration
You can call worker agents directly for specific tasks. `oneproc` wraps these calls to capture metadata and git diffs.

```bash
python -m oneproc.cli worker ask --agent gemini --task "Draft a theoretical mapping for epsilon-rho coupling"
```

### C. Paper Validation
Validate an existing technical paper against the governance template and claim requirements.

```bash
python -m oneproc.cli validate-paper check path/to/paper.md --level C4 --intent validate
```

**Subcommands:**
- `check`: Return pass/fail summary.
- `explain`: Return detailed failure explanations and required fixes.
- `json-report`: Emit machine-readable validation report.

## 4. Governance Gates (V2)
`oneproc` V2 enforces hardened gates:

| Gate | Requirement | Action on Failure |
| --- | --- | --- |
| **Template V2** | Sections must not be empty or contain placeholders; Conclusion must start with "Within these models...". | **BLOCK** |
| **Consistency** | Metadata (e.g., measurement count, models used) must match the paper body. | **BLOCK** |
| **Falsification** | C4+ requires valid falsification vectors (FV-1..FV-4). | **BLOCK** (Strict) or **DOWNGRADE** |
| **Measurement V2** | C4+ requires measurement sections and quantitative results in the body. | **DOWNGRADE** |
| **Intent Policy** | Claims are capped by intent (`explore`: C2, `validate`: C5, `publish`: C6). | **DOWNGRADE** |

## 5. Trace Capture & Auditability
Every execution of `oneproc` generates a unique `run_id` and a corresponding trace log located in:
`outputs/runs/<run_id>/trace_<run_id>.json`

This trace captures:
- Component activity (Orchestrator, Validators, Workers).
- Input parameters and output results.
- Subprocess stdout/stderr and git diffs.
- Detailed governance decision paths.

## 6. Directory Structure
- `oneproc/`: Core implementation.
- `registry/`: Governance authority files (Lexicon, Tool Manifest, etc.).
- `outputs/runs/`: Governed run outputs and trace logs.
- `patches/`: Durable worker-generated patches.

---
*Note: Conclusions for all empirical papers generated via `oneproc` MUST begin with: **“Within these models…”***
