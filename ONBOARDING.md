# Acellorator — Onboarding (honest + humble)

Acellorator is a **governed research workspace** for exploring and stress-testing ideas related to *“The Law of the One Process”* using **multiple simulation engines**, shared experiment configs, and reproducible outputs.

It is best read as a lab notebook that is being actively structured into a more formal system: some parts are polished; others are still scaffolding.

## What this project is (and isn’t)

- It **is** a place to run model experiments across different *mechanism classes* (e.g., reaction–diffusion, agent-based, cellular automata, graph dynamics) and compare observables.
- It **is** opinionated about governance: terminology, evidence provenance, and claim strength are intentionally constrained.
- It **is not** a guarantee of “truth” about the world. When the repo says “supported,” it should be read as “supported **within these models and protocols**,” not as a universal statement.
- It **is not** a single monolithic simulator. Think “ecosystem + workflow” rather than “one engine.”

## How to get value quickly

1. Read the governance narrative and rules of the road:
   - `docs/governance/NARRATIVE.md`
   - `docs/governance/AGENTS.md`
2. Skim usage guides (choose what matches what you’re doing):
   - `USAGE.md`
   - `USAGE_ONEPROC.md`
   - `USAGE_LEXICON.md`
3. Pick a small, reproducible run to start with:
   - `configs/` contains example configs
   - `outputs/` is where recoverable run artifacts go

If you’re new, prefer running an existing config end-to-end before changing anything.

## Repository map (practical mental model)

- `tools/`: the engines and analysis tools (often with `validation/` evidence)
- `configs/`: experiment configs (prefer creating new configs over editing defaults)
- `scripts/`: orchestration, governance checks, and report tooling
- `outputs/`: run artifacts intended to be recoverable and auditable
- `registry/`: canonical manifests, lexicon, and compliance artifacts
- `docs/`: narrative, theory notes, and paper-like writeups
- `reports/`: audits and tool rigor summaries

## Evidence and claim strength (what “governed” means here)

This project tries to avoid two common failure modes:

- **Overreach:** treating a model behavior as a universal fact.
- **Single-mechanism lock-in:** treating one engine’s update rule as the whole story.

The working norm is:

- Prefer **mechanism independence** over “more runs of the same tool.”
- Prefer **recoverable outputs** over screenshots or uncited claims.
- Prefer **explicit observables and falsification conditions** over metaphor.

## Terminology note (read gently)

The repo uses a specialized vocabulary (e.g., *epsilon*, *residue*, *rho*, *coupling/CSI*, *admissibility*). These terms can overlap with standard physics words but are not guaranteed to mean the same thing. When in doubt:

- treat definitions as **operational** (what is measured / what changes under what rule),
- and look to `registry/` for canonical mappings and validation status.

## If you want to contribute (safe defaults)

- Add new experiments by creating **new config JSON** in `configs/` and writing outputs to a **new** run directory under `outputs/`.
- Avoid editing engine/core simulation logic unless you explicitly intend to do engine development.
- When writing new docs or papers, keep claims scoped and start conclusions with **“Within these models…”**.

## Where to look if something feels “too strong”

If a document sounds more confident than the evidence trail suggests, the best next step is usually to locate:

- the run artifacts under `outputs/`,
- the tool’s `validation/` materials (if present),
- the governance/claim gate script outputs (if present),
- and whether the result was cross-checked in a different mechanism class.

That is not a criticism of the text—just a reminder of the project’s bias toward evidence you can rerun.

