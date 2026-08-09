# Independence Audit

## Independence Audit Summary

This audit evaluates the independence of the verification methods used for each attack campaign in this workspace.

* **Audit Date:** 2026-08-04
* **Assessor:** Antigravity (AI research assistant)
* **General Status:** `SAME_SCRIPT_DUAL_COMPARISON` (Dual Program M and S comparisons are co-located in the same execution files).

---

## Campaign Independence Classification

| Campaign ID | Verification Method | Independence Classification | Notes / Assessment |
| :--- | :--- | :--- | :--- |
| **FAT-01 through FAT-13** | Legacy report-only | `REPORTED_NOT_REPLAYED` | Verification status relies on historical reports. |
| **FAT-14** | Connectedness vs Clique check | `SAME_SCRIPT_DUAL_COMPARISON` | Dual topological comparison in the same file. |
| **FAT-15 through FAT-24** | Dual MTO-OTM vs standard math checks | `SAME_SCRIPT_DUAL_COMPARISON` | Program M (native) and Program S (standard math) are co-located in the same script. Design dependencies are shared. |

---

## Independence Rules Applied

1. **SAME_SCRIPT_DUAL_COMPARISON Rule:** Co-locating Program M and Program S in the same script shares author dependencies and execution paths, and is classified as `SAME_SCRIPT_DUAL_COMPARISON` rather than `INDEPENDENTLY_VERIFIED`.
2. **Indexing vs Primitive Distinguishability:** Program S relies on index sets (e.g. $(a, 1)$ vs $(a, 2)$) to keep identical capacities distinct. This represents a projection loss compared to the native role-based distinction, which requires separate external mathematical formalization to establish independence.
