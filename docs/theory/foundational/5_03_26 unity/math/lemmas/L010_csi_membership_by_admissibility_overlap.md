# L010 — `csi(α)` Membership by Admissibility Overlap (G3, conditional)

## Statement
Assume each process index `α` has an admissibility window `Aα` (evaluated under a fixed residue context), and define coupling-neighborhood membership by mutual admissibility overlap:

`β ∈ csi(α)  ⇔  Aα ∩ Aβ ≠ ∅`.

Then `csi(α)` is fully determined by the collection of windows `{Aγ}` and is therefore a **derived** object (not a primitive topology), subject to the same residue evaluation context used in the core biconditional.

## Dependencies
- Source alignment:
  - `TN_Admissibility_Window_and_Local_R.txt` (explicitly proposes overlap-induced interaction topology)
  - `TN_MLaw_Derivation_v01.extracted.txt` (Gap 3: closed CSI membership rule; candidate overlap)
- Assumptions:
  - A1 (Well-typedness)
  - windows are evaluated under a fixed residue evaluation context (so overlap is well-posed)
- Prior lemmas: none

## Proof sketch
This is definitional: given the rule, membership is computed from window overlap. The only substantive requirement is residue-context consistency (fixed evaluation context) so that "overlap" is not time-shifted across contexts. ∎

## Status
draft

## Supersedes / Superseded-by

## Metadata (Migrated from LAW-004)
- **Law Conditions:**
  - CSI_domain_explicit
  - summation_index_beta_explicit
  - CSI_weighting_explicit
  - orientation_kernel_explicit
  - finite_flux_condition_explicit
  - decay_or_truncation_condition_explicit
  - projection_into_A_alpha_required_or_failure_preserved
  - no_global_convergence_claim
- **Failure Modes:**
  - unbounded_CSI_summation
  - transport_flux_divergence
  - weighting_kernel_collapse
  - orientation_kernel_overconstraint
  - hidden_global_convergence_claim
  - projection_failure_after_transport
  - nonlocal_transport_fragmentation
  - physics_claim_leakage

