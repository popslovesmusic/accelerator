# Additive-Only Workflow (Proof/Lemma-First) — This Directory

**Scope:** `docs/theory/foundational/5_03_26 unity/math/`

**Rule:** From this point forward, work in this directory is **additive only**:
- Do **not** edit existing files (including earlier lemmas/proofs), except to fix encoding/corruption that prevents reading.
- All new work is added as **new files** with new IDs.
- If a prior statement needs revision, create a **new lemma/proof note** that supersedes it (never overwrite).

---

## 1) File types (what gets added)

- `NN_entry_*.md` — entry-level documents (like `01_entry_lemmas_and_proofs.md`).
- `lemmas/LNNN_*.md` — individual lemmas (one lemma per file, stable ID).
- `proofs/PNNN_*.md` — longer proofs that reference lemma IDs.
- `notes/NNNN_*.md` — informal notes that may later be promoted into lemma/proof files.
- `REGISTRY_*.md` — append-only registries (see below).

---

## 2) Stable IDs and naming

Use stable identifiers so later documents can cite without ambiguity.

- Lemmas: `L001`, `L002`, …
  - File: `lemmas/L001_<slug>.md`
- Proofs: `P001`, `P002`, …
  - File: `proofs/P001_<slug>.md`

Slugs should be short, lower_snake_case.

---

## 3) “Proof-first” structure (required sections)

Every lemma file MUST include:
1. **Statement** (precise)
2. **Dependencies** (definitions/assumptions/other lemmas)
3. **Proof** (or **Proof sketch** if intentionally partial)
4. **Status** (`draft | conditional | complete`)
5. **Supersedes / Superseded-by** (optional; for additive revisions)

Every proof file MUST include:
1. **Goal**
2. **Uses** (lemma IDs)
3. **Proof**
4. **Status**

---

## 4) Registries (append-only indices)

Additions go through registries so the “entry” stays navigable without editing old text.

- `REGISTRY_lemmas.md` — append-only list of lemmas + one-line summary + dependencies.
- `REGISTRY_proofs.md` — append-only list of proofs + which lemmas they use.

When a lemma is superseded, add a new line in the registry noting the superseding lemma (do not edit the old entry).

---

## 5) Additive revision protocol

If a lemma is wrong/unclear:
- Create a new lemma with a new ID (e.g. `L014`).
- In the new lemma file, include `Supersedes: L006`.
- Append a line to `REGISTRY_lemmas.md` noting “`L006` superseded by `L014`”.

No edits to `L006`.

---

## 6) Current entry points

- `00_series_alignment.md` — how the documents relate.
- `01_entry_lemmas_and_proofs.md` — minimal definitions + initial lemmas.

