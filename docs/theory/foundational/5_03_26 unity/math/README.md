# Unity / Math (Foundational Entry) — 2026-05-05

This directory is the **entry point into math** for the local “Mono-Process Framework — Theoretical Foundations Series”.

The organizing object is the **core residue-conditioned biconditional update expression** (as captured in the working note and formalized in the derivation note). All mathematical development here is structured as **lemmas and proofs** built additively from that expression, with assumptions and gaps made explicit.

---

## What’s here (start here)

- `01_entry_lemmas_and_proofs.md` — minimal definitions + initial lemma/proof sketches (entry overview).
- `lemmas/` — one lemma per file, stable IDs `L001…`.
- `proofs/` — longer proofs, stable IDs `P001…` (not yet populated beyond templates).
- `REGISTRY_lemmas.md` — append-only index of lemma IDs.
- `REGISTRY_proofs.md` — append-only index of proof IDs.
- `PROOF_PLAN.md` — planned proof path `P001…` and which gap-closures they require.
- `WORKFLOW_ADDITIVE_ONLY.md` — governance for this directory: **additive only** (no edits to existing files).

Primary source notes (inputs to the entry system):
- `(ℰ ≠ 0) ⇔ δ(ℰ  0).txt` — working capture of the core expression + M-law list + variable-role notes.
- `TN_MLaw_Derivation_v01.docx` — derivation note claiming M-laws are generable from the core expression (theoretical).
- `TN_MLaw_Derivation_v01.extracted.txt` — plain-text extract of the `.docx` for grep/diff.
- `TN_Admissibility_Window_and_Local_R.txt` — companion note separating `Aα`, `Π_Aα`, selection `O*`, and induced local reference `−(i)α`.
- `00_series_alignment.md` — “glue” note aligning notation and dependencies across the three sources.

---

## Core stance (how to read the math)

The core expression is read as a **residue-conditioned biconditional**:
- `⇔_R` is not a bare logical equivalence; it is a **history-gated two-way constraint**.
- Lemmas/proofs must specify which side is assumed “active/evaluated” in a given argument and must preserve closure under the same residue context.

This directory stays **mechanism-independent** at entry level: the goal is structural results that do not depend on committing to a single mechanism class (ODE/PDE/CA/etc.).

---

## Additive-only workflow (required)

This directory is **additive only**:
- Do not edit existing files to “fix” wording or change results.
- Add new lemma/proof files with new IDs.
- If something needs revision, add a new lemma/proof that **supersedes** the old one and record the supersession in the registries.

Details: `WORKFLOW_ADDITIVE_ONLY.md`.

---

## How to contribute a new lemma or proof

- New lemma:
  - Copy `lemmas/LEMMA_TEMPLATE.md` → `lemmas/LNNN_<slug>.md`
  - Fill: Statement, Dependencies, Proof/Sketch, Status
  - Append a new line to `REGISTRY_lemmas.md`

- New proof:
  - Copy `proofs/PROOF_TEMPLATE.md` → `proofs/PNNN_<slug>.md`
  - List lemma IDs used
  - Append a new line to `REGISTRY_proofs.md`

---

## Known gap-closures (explicit, tracked)

Stronger results are intentionally blocked until these are defined:
- **G1:** oriented structure for `Aα` sufficient to derive `orientation` / `−(i)α`
- **G2:** explicit definition of `transport(·,·)` sufficient for propagation identities
- **G3:** closed membership rule for `csi(α)` (candidate: admissibility overlap)

See: `PROOF_PLAN.md`.

