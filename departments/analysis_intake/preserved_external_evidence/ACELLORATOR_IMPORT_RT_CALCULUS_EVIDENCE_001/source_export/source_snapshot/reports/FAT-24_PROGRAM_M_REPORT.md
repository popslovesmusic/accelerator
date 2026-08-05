# Program M Falsification Report: FAT-24

## 1. Native Equivalence Predicate Definition

Two triplets are equivalent under the native predicate if they preserve the same symmetry reference target, left/right complementary orientation roles, and capacity parameters.

## 2. Invariants Report

* **Preserved Invariants:** Symmetry reference target, left/right orientation roles, capacity sum.
* **Broken Invariants:** Admissibility deformation changes activity trajectories; reorientation changes the observed slice.
* **Identity Capacity Status:** Preserved under structural replay; shifts to STRUCTURALLY_EQUIVALENT under capacity parameter changes.
* **Phase Signature Status:** Erased under many-to-one MTO closure; OTM is reconstructive and does not recover historical pre-closure state.

## 3. Test Log

* **M1 (Replay):** IDENTICAL
* **M2 (Reversal):** DUAL_OR_INVERSE
* **M3 (Reorientation):** Preserved
* **M4 (Substitution):** NON_EQUIVALENT
* **M5 (Deformation):** Preserved
* **M6 (Decoupling):** Retained (activity drops to zero in decoupled domain but identity is unchanged)
* **M7 (Alias):** Distinct
* **M8 (Closure Alias):** Confirmed
* **M9 (OTM Reconstruction):** Confirmed
* **M10 (Capacity Deformation):** STRUCTURALLY_EQUIVALENT
