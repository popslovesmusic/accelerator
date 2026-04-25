# Strict Procedural Monism: Lexicon and Terminological Map
**Date:** April 19, 2026
**Status:** Human-Readable Synthesis

This document consolidates the project's terminological infrastructure, bridging formal canonical definitions, shorthand aliases, and emerging candidates.

---

## I. Core Canonical Terms
These terms represent the stabilized, high-integrity pillars of the SPM framework.

| Canonical Term | Occurrences | Note |
| :--- | :--- | :--- |
| **NOT_axiom** | 22 | Primary prohibition of the null state ($\varepsilon \neq 0$). |
| **PDE_process_dynamics** | 34 | Formal mathematical modeling of process evolution. |
| **DOF_eff** | 17 | Effective degrees of freedom within a stabilized basin. |
| **cognition_SRC** | 7 | Structural Recursive Cognition / Self-Referential Residue. |
| **IGSOA_framework** | 9 | Integrated Global Symmetry Orientation Array. |
| **DFVM_framework** | 2 | Discrete Functional Viability Mapping. |

---

## I.a Operational Canonicals (Promoted For Validation)
The following terms were promoted to `canonical_term` status to support the **Lexicon Validation Program** and enable governed, role-specific operational definitions:

- **epsilon** — operational mismatch / driver signal (validated by role in `lexicon_validation_registry.json`).
- **rho** — participation / activity readout (promoted for consistency; role validation remains open).
- **residue** — accumulated constraint state (validated by role as admissibility gate).
- **admissibility** — filter / continuation acceptance (validated by role as residue-gated filter).
- **continuation** — candidate vs admissible transition (partially verified by role; broader semantics remain open).
- **mismatch** — surface-form for epsilon in many tools (promoted for translation consistency).
- **coupling** — interaction reach / CSI (validated by role as synchrony gain control).

These are operational canonicals: they are not metaphysical primitives; their “verification” refers to **within-model operational support** with recoverable artifacts, and charter-aware claim classification.

---

## II. Technical Alias Map (High Signal)
The following mappings are enforced to ensure that shorthand and common language are correctly resolved to the SPM engine's formal logic.

| Shorthand / Alias | Canonical Resolution |
| :--- | :--- |
| **NOT** | NOT_axiom |
| **PDE** | PDE_process_dynamics |
| **DOF** | DOF_eff |
| **SRC** | cognition_SRC |
| **IGSOA** | IGSOA_framework |
| **DFVM** | DFVM_framework |
| **admissibility** | admissibility |
| **residue** | residue |
| **mismatch** | mismatch |
| **orientation** | orientation |
| **basin** | basin |
| **ε** | epsilon |
| **varepsilon** | epsilon |
| **ρ** | rho |
| **R** | residue |
| **CSI** | coupling |
| **csi** | coupling |

*(Note: The full alias map contains over 700 standardizations, including mathematical symbols like **$\varepsilon$**, **$\rho$**, and **$R$**.)*

---

## III. Emerging Terminology (Gap Queue Sample)
The following terms have been identified across the corpus as highly frequent and are currently undergoing formal definition for promotion to "Canonical" status.

| Term | Document Count | Proposed Role |
| :--- | :--- | :--- |
| **continuation** | 53 | Fundamental operation mandate ($\rho$). |
| **residue** | 33 | Persistent historical trace ($R$). |
| **admissibility** | 27 | Constraint-based candidate filtering ($\mathcal{A}$). |
| **phase** | 26 | Relational state of oscillatory modes. |
| **process** | 26 | The singular ontological primitive. |
| **orientation** | 24 | Local preferred direction operator ($-(i)$). |
| **identity** | 11 | Persistent recurrence of stabilized structure. |
| **regime** | 11 | Dominance-ordered behavioral zones. |

---

## III.a Validation Registry (Charter-Aware)
Role-specific validation status is tracked in:

- `lexicon_validation_registry.json`

This registry records:

- Evidence levels `L0–L3` for **operational roles** (not global metaphysical truth).
- Compliance charter metadata and **data provenance citations** for any empirical support.

Important: Under **Compliance Charter v2.3** (`theory/lexicon/compliance_charter_v2_3.json`), empirical claims must cite recoverable source files and may require v2.3 metric schema compliance for “verified” status. The registry therefore distinguishes:

- **Operational support (within these models)**: recoverable artifacts + multi-model/multi-seed + falsification where applicable.
- **Charter claim classification**: a conservative tag (`verified`/`theoretical`/`provisional`/`prior_finding`) applied to how the claim may be written in documents.

---

## IV. Lexicon Maintenance & Governance
The lexicon is managed according to the following internal rules:
*   **Monistic Enforcement:** Terms that imply independent "objects," "fields," or "time" are flagged as candidates for reduction or rejection.
*   **Automatic Promotion:** Candidate terms with high document frequency and clear semantic alignment are prioritized for canonicalization.
*   **Noise Filtering:** Common non-technical terms are sequestered to maintain the "Lexicon Lock" on the operational engine.
*   **Compliance Charter v2.3:** All lexicon updates and all technical papers must follow `theory/lexicon/compliance_charter_v2_3.json`, including data provenance requirements for empirical assertions.

---

**Source Files:**
*   `lexicon_canonical.json` (9,191 lines)
*   `lexicon_alias_map.json` (809 lines)
*   `lexicon_gap_queue.json` (9,040 lines)
