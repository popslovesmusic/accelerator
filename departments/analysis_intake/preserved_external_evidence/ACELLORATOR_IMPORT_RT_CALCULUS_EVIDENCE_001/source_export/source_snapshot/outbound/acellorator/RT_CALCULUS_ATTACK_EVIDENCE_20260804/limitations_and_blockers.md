# Limitations and Blockers

This document records all blockers, representation boundaries, and verification limitations identified during the preparation of the falsification evidence bundle.

## Active Blockers

| Blocker ID | Severity | Target Attacks | Description |
| :--- | :--- | :--- | :--- |
| **SAME_SCRIPT_VERIFICATION** | Critical | FAT-15 through FAT-24 | Program M and Program S are implemented inside the same script/execution unit, sharing the same author's design dependencies. This does not constitute independent verification. |
| **MISSING_DEPENDENCY_LOCK** | Resolved | New replay runs | `requirements.lock` is now present and included in the refreshed frozen snapshot. Historical runs were not executed under this lock unless their records say so. |
| **MISSING_STDOUT_STDERR** | Medium | FAT-01 through FAT-14 | Legacy runs did not capture raw terminal output streams (`stdout.txt`/`stderr.txt`). |
| **MISSING_ENVIRONMENT_RECORD** | Medium | FAT-01 through FAT-14 | Legacy runs did not record platform, CPU, or Python interpreter metadata. |
| **UNRESOLVED_CLAIM_SCOPE** | Medium | FAT-01 through FAT-24 | Multiple historical reports employ overstrong language (e.g., "proves", "validated", "verified") which must be scope-corrected to model-relative or representation-relative claims. |
| **PARTIAL_RUN_CAPTURE** | Medium | FAT-15 through FAT-24 | Immutable run capture is operational, but only the FAT-22 validation run is currently captured in `run_outputs`; the remaining campaigns require replay under the current logger. |
| **PACKAGE_NOT_SUBMITTED** | Informational | Evidence package | The refreshed package is intentionally not submitted to Acellorator Analysis Intake by user instruction. |

## Representation Boundaries & Information Loss

* **Set-Theoretic Coordinate Injection:** In standard posets and categories, representing identical elements requires explicit coordinate or index injection, which is absent from native RT capacity slots.
* **Ternary Decomposability Loss:** Decomposing the ternary reference-centered triplet into binary pairs loses joint Complementary Orientation dependency.
* **Bisimulation Collapse:** Conventional observational-equivalence models collapse structural aliases and pre-closure phase signatures, leading to representation collapse.
