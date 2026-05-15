# Stable Basin Proof-Eligibility Filter (MPF-PF-016)

## 1. Purpose
This document defines the **proof-eligibility filter** for local admissibility basins classified in MPF-PF-015. It identifies which stable basins may support restricted local proof steps while explicitly blocking ineligible basins (metastable, oscillatory, severed, or ambiguous) from being used in formal derivation.

## 2. Eligibility Criteria
A basin is classified as **PFE-ELIGIBLE-LOCAL** only if it satisfies all of the following:
- **Stability**: `basin_class` must be `RSB-STABLE`.
- **No Activation**: No `failure_geometry` modes are triggered.
- **Budget**: Admissibility budget remains non-exhausted throughout recursion.
- **Identity**: Identity trace is unique and unambiguous.
- **Grammar**: LAW034 local composition rules pass or restricted-pass.
- **Scope**: Explicitly restricted to `STRICTLY_LOCAL_RESTRICTED_DOMAIN`.

## 3. Ineligibility Criteria (Blocked)
A basin is classified as **PFE-INELIGIBLE-BLOCKED** or **PFE-INELIGIBLE-METASTABLE** if:
- `basin_class` is `RSB-METASTABLE`, `RSB-OSCILLATORY`, `RSB-SEVERED`, or `RSB-AMBIGUOUS`.
- Any preserved blocker (divergence hotspot, threshold sensitivity) is triggered.
- Global composition or universal persistence is required.
- Physics claim dependency is detected.

## 4. Output Classes
- **PFE-ELIGIBLE-LOCAL**: Eligible for restricted local proof-step use only. Promotion blocked.
- **PFE-INELIGIBLE-BLOCKED**: Blocked by preserved failure or excluded domain.
- **PFE-INELIGIBLE-METASTABLE**: May support empirical trace, not symbolic proof.
- **PFE-REVIEW-REQUIRED**: Status unclear; requires manual audit.

## 5. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Proof Status**: LTC_eligibility_filtering_only.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.

---
[Back to Master Index](codex_master_index.md)
