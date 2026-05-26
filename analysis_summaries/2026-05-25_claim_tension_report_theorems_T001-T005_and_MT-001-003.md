# Claim Tension Report: Foundational Theorems (T001–T005) and Local Minimal Theorems (MT-001–MT-003)

**Date:** 2026-05-25  
**Mode:** Audit (documentation artifact only)  
**Evidence class:** C0 (indexing + path existence checks only; no reruns, no new measurements)  

## 1. Scope
This report inventories theorem locations and compares:

1. Theorem documents’ self-declared status (e.g., “formally_proven”, “C6”).
2. Evidence paths cited by those theorem documents and whether the referenced artifacts exist on disk.
3. Alignment (or lack thereof) with governance registries that centrally track claims and claim ceilings.

This report does **not** certify correctness of the theorems, does **not** elevate any claim level, and does **not** infer external physical truth. It records repository-internal consistency signals and tensions.

## 2. Directly Observed (files, paths, and stated text)

### 2.1 Theorem locations (5 foundational)
- `docs/theory/foundational/5_03_26 unity/math/theorems/T001_knot_theorem.md`
- `docs/theory/foundational/5_03_26 unity/math/theorems/T002_meta_bridge_symmetry.md`
- `docs/theory/foundational/5_03_26 unity/math/theorems/T003_web_theorem.md`
- `docs/theory/foundational/5_03_26 unity/math/theorems/T004_hierarchical_stabilization.md`
- `docs/theory/foundational/5_03_26 unity/math/theorems/T005_minimizer_switching_stability.md`

### 2.2 Theorem locations (3 local minimal)
- `proofs/MT-001/proof.md`
- `proofs/MT-002/proof.md`
- `proofs/MT-003/proof.md`
- Consolidated registry: `registry/math/minimal_theorems_registry.json`

### 2.3 Evidence path existence checks (referenced by theorem documents)

| Theorem | Referenced evidence path (as cited) | Exists on disk |
|---|---|---|
| T001 | `results/2026-05-21_run06_Global_Persistence_Scaling/paper.md` | Yes |
| T001 | `results/2026-05-24_run01_interaction_hierarchy_falsification/metrics.json` | Yes |
| T002 | `results/2026-05-23_run06_MSV_001_Cross_Model_Verification/paper.md` | Yes |
| T002 | `results/2026-05-24_campaign_interaction_hierarchy_falsification/metrics.json` | **No** |
| T003 | `results/2026-05-21_run05_Relational_Reach_Validation/paper.md` | Yes |
| T003 | `results/2026-05-24_campaign_interaction_hierarchy_falsification/metrics.json` | **No** |
| T004 | `results/2026-05-21_run06_Global_Persistence_Scaling/paper.md` | Yes |
| T004 | `results/2026-05-24_campaign_interaction_hierarchy_falsification/metrics.json` | **No** |
| T005 | `results/2026-05-23_run06_MSV_001_Cross_Model_Verification/paper.md` | Yes |

### 2.4 Observed registry coverage

- `registry/claim_registry.json` currently tracks the claim object `L5_RIGOR_FORKED_ATTACK` with a recorded gate downgrade to `proposed_interpretation`.
- `registry/claim_support_matrix.json` contains a governed claim entry for MST-001 (`PCD-CLM-MST-001`) with explicit execution-plan dependencies and claim ceilings.
- `registry/math/minimal_theorems_registry.json` marks MT-001..MT-003 with `claim_boundary: formal_procedural_only` and conditional/local closure statuses.

### 2.5 Observed falsification targeting signals
- `results/2026-05-24_run01_interaction_hierarchy_falsification/falsification_summary.json` explicitly lists `MT-001`, `MT-002`, `MT-003` as targets within a Phase 3 baseline suite.
- `results/2026-05-23_run12_BLOCK_CLOSURE_X_Attack/paper.md` records an adversarial attack on MST-001 and concludes “overall result is FALSIFIED” (repository-internal statement, scoped to that report).
- `results/2026-05-23_run14_RES-LIMIT-01/paper.md` states further mapping is required “to move MST-001 to C6” (repository-internal statement, scoped to that report).

## 3. Inferred Inside the Framework (bounded, internal consistency only)

### 3.1 Two-layer theorem semantics (internal taxonomy tension)
Within repository structure, “theorem” appears to be used in at least two non-identical ways:

1. **Local minimal theorem packages (MT-001..003)**: explicitly conditional/local and bounded to “formal_procedural_only” in the consolidated registry.
2. **Foundational theorems (T001..T005)**: documents self-declare “formally_proven” / “Rigor Level: C6”, and cite C5 evidence paths, but are not centrally tracked as first-class claim records in `registry/claim_registry.json` (as currently populated).

This is an internal-documentation consistency observation, not a claim about mathematical invalidity.

### 3.2 MST-001 (T005) is the strongest internal tension point
T005 asserts `Rigor Level: C6`, while (a) the claim-support matrix treats MST-001 as a conditional claim with execution-plan ceilings, and (b) at least one adversarial report concludes “FALSIFIED” under a specific falsification vector and (c) a resolution-frontier report states more work is needed to reach C6.

Interpreting these together suggests MST-001 is not uniformly “closed” across the repo’s governance artifacts.

## 4. External Resemblance (analogy only)
Not assessed in this report.

## 5. What this does NOT prove
- It does not prove any theorem statement is correct or incorrect.
- It does not prove evidence in `results/` supports the associated theorem claims beyond existence of referenced files.
- It does not grant permission to elevate claims or publish at C6.
- It does not establish any external physical correspondence.

## 6. Failure Modes / Uncertainty
- **Path drift:** The missing `results/2026-05-24_campaign_interaction_hierarchy_falsification/metrics.json` suggests either a renamed directory, a stale link, or a consolidation mismatch.
- **Registry incompleteness:** `registry/claim_registry.json` may be intentionally minimal (tracking only certain publication intents), so “absence of theorem claim records” there may be policy-driven rather than omission.
- **Semantic overload of “C6”:** Some documents use “C6” as a target or rhetorical label; governance may intend “C6” to require a specific gate path (`scripts/governance_gate.py`) and claim registry entry.

## 7. Recommended Next Actions (governed, non-escalatory)
1. Decide the canonical “claim tracking surface” for T001–T005: either add formal claim entries (with gate checks) or explicitly mark these theorem docs as “narrative / not gated”.
2. Repair or supersede the missing evidence reference(s) to `results/2026-05-24_campaign_interaction_hierarchy_falsification/metrics.json` (if a replacement path exists).
3. For MST-001, reconcile T005’s “C6” label with:
   - `registry/claim_support_matrix.json` execution-plan ceilings, and
   - outcomes and scope limits recorded in `results/2026-05-23_run12_BLOCK_CLOSURE_X_Attack/paper.md` and `results/2026-05-23_run14_RES-LIMIT-01/paper.md`.

