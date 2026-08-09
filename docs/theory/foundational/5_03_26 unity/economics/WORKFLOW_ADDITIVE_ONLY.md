# Additive-Only Workflow — Economics Program

**Scope:** `docs/theory/foundational/5_03_26 unity/economics/`

To maintain historical residue and prevent ontology drift, all developments in this directory must strictly adhere to the **additive-only rule**:

1. **No Overwrites:** Do not edit existing definition, lemma, or proof files once they have been registered.
2. **New IDs:** All new developments, lemmas, or proofs must be written as new files with unique, stable IDs (e.g., `ECON-001`, `ECON-L001`, `ECON-P001`).
3. **Supersession Protocol:** If a prior definition, metric form, or law needs revision, write a new file detailing the modification and specify `Supersedes: <Old_ID>`.
4. **Registry Sync:** Every addition must be logged in `REGISTRY_economics.md` and synced with `registry/economics/theorem_status_registry.json`.

---

## Naming Standards

- **Conceptual/Induction Entries:** `ECON-NNN_<slug>.md`
- **Lemmas:** `lemmas/ECON-LNNN_<slug>.md`
- **Proofs:** `proofs/ECON-PNNN_<slug>.md`
- **Notes:** `notes/ECON-NNNN_<slug>.md`
