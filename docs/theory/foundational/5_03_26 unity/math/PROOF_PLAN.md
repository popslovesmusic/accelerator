# Proof Plan (Additive, Proof/Lemma-First) — 2026-05-05

**Scope:** `docs/theory/foundational/5_03_26 unity/math/`

**Workflow rule:** This plan is additive-only. If it changes, add a dated addendum section at the end (do not rewrite earlier entries).

---

## 0) Current foundation (already in place)

- Entry overview: `01_entry_lemmas_and_proofs.md`
- Lemma files: `lemmas/L001_*.md` … `lemmas/L005_*.md`
- Registries: `REGISTRY_lemmas.md`, `REGISTRY_proofs.md`

Known gap-closures to unlock stronger results:
- **G1:** oriented structure for `Aα` sufficient to derive `orientation` (the `−(i)` mechanism)
- **G2:** explicit definition of `transport(·,·)` sufficient for propagation/transport identities
- **G3:** closed membership rule for `csi(α)` (candidate: admissibility overlap)

---

## 1) Near-term proof targets (no new primitives required)

### P001 — “Entry Theorem” (core structural consequences)
**Goal:** Package L001–L005 into a single coherent theorem showing:
- update increments are admissible,
- empty neighborhood implies fixed point,
- admissibility filtering is pre-update,
- closure must be read residue-conditionally.

**Uses:** L001, L002, L003, L004, L005  
**Requires:** no gap closures (G1–G3 remain explicit limits)  
**Output file:** `proofs/P001_entry_structural_consequences.md`

---

## 2) Proof targets unlocked by specific gap closures

### P002 — Orientation-from-window construction (closes G1)
**Goal:** Given an explicit oriented structure on `Aα`, construct a well-defined `orientation(α)` / `−(i)α` object and prove it is induced by selection under mismatch (not a primitive input).

**Uses:** L001, L005 (and new lemmas to be added after G1 definition)  
**Requires:** G1  
**Output file:** `proofs/P002_orientation_from_A_window.md`

### P003 — Transport identity / propagation law (closes G2)
**Goal:** With a defined `transport(·,·)`, prove a compositional or frame-consistency identity that justifies a “propagation” statement (the math core needed for an M8-type reading).

**Uses:** L001, L004, L005 (and new transport lemmas)  
**Requires:** G2  
**Output file:** `proofs/P003_transport_propagation_identity.md`

### P004 — Neighborhood closure from admissibility overlap (closes G3)
**Goal:** Assuming (or proving) a rule like `β ∈ csi(α) ⇔ Aα ∩ Aβ ≠ ∅` under residue context, prove `csi(α)` is dynamically induced and compatible with the residue-conditioned closure constraint.

**Uses:** L002, L005 (and new lemmas relating `Aα` to `csi`)  
**Requires:** G3 (and likely partial G1)  
**Output file:** `proofs/P004_csi_closure_from_admissibility_overlap.md`

---

## 3) Registry updates when proofs are written

When any `P00N` file is added:
1. Add the proof to `REGISTRY_proofs.md` (append a new line).
2. If new lemmas were introduced, add them to `REGISTRY_lemmas.md` (append-only).

