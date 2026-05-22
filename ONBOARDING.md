# Onboarding: The Mono-Process Framework (MPF)

Welcome to the Acellorator research environment. You are operating within the **Calculus of Distinction**, a formal relational grammar for multiscale process research.

## 1. Governance Authority
- **Authority:** The project-local `GEMINI.md` is the active execution authority.
- **Narrative:** `MATH_PROGRAM_NARRATIVE.md` traces the genesis of the theory to its current **Level C6 Formal Closure**.
- **Charter:** `registry/compliance_charter_v2_3.json` governs all claims, translations, and data provenance.

## 2. Core Laws (The Master Set)
Every researcher and agent must adhere to the four foundational pillars:
1.  **3-Peak Rule (T001):** Stability requires $N \ge 3$; complexity is a necessity.
2.  **Singularity Rebound (SING-001):** Singularity is a recursive trigger state, not an endpoint.
3.  **Tertiary Node Structure (L043):** Persistence requires functional partitioning into $\{I, O, R\}$.
4.  **Topology-Geometry Biconditional (L045):** Geometry is emergent relational accessibility.

## 3. Standard Workflows

### 3.1 Mathematical Development (Additive-Only)
- **Location:** `docs/theory/foundational/5_03_26 unity/math/`
- **Rule:** Never modify existing lemmas/proofs. Create new files and declare them `Supersedes: [OLD_ID]`.
- **Sync:** Run `python scripts/sync_math_registry.py` after adding math objects.

### 3.2 Research Campaigns
- **Output:** All results must be saved in `results/YYYY-MM-DD_runNN_name/`.
- **Hygiene:** Every run must contain a `data/` and `artifacts/` subdirectory.
- **Reporting:** Every campaign must produce a `paper.md` using the 11-section governed template.

### 3.3 Lexicon Induction
- Missing terms must be added to `registry/lexicon_gap_queue.json` as `GAP_OPEN`.
- Promotion to `L2 (Partially Verified)` requires evidence recorded in `registry/lexicon_validation_registry.json`.

## 4. Verification & Validation
- **Global Validate:** Run `./run_global_validation.bat` before any commit.
- **Claim Gate:** Use `scripts/governance_gate.py` to classify research papers.

## 5. Publication
- Official results are exported as **Zenodo Publication Bundles** in the `zenodo/` directory.
- Bundles must include a SHA256 `provenance_manifest.json` for all data and artifacts.

---
**Status:** ARCHIVAL READY
**Compliance:** Charter v2.3
