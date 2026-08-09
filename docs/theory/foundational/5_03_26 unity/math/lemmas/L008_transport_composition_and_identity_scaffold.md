# L008 — Transport Composition + Identity Scaffold (G2)

## Statement
Assume the transport operator `transport(·,·)` (aka `Nav_T(·,·)`) is defined between reference-bearing states (e.g., `ωα` or derived `-(i)α`) and that it supports:

1) an **identity** element for self-transport, and
2) a **composition** rule along chains.

Formally, assume there exists a composition operator `∘` such that for admissible triples `(α,β,γ)` under the current residue context:

- (Identity) `transport(ωα, ωα) = e` where `e` is neutral for `∘`
- (Chain composition) `transport(ωα, ωγ) = transport(ωα, ωβ) ∘ transport(ωβ, ωγ)`

Then the framework has the minimal algebraic structure needed to treat "propagation" as transport composition (G2 scaffold).

## Dependencies
- Source alignment:
  - `TN_MLaw_Derivation_v01.extracted.txt` (Gap 2: explicit `Nav_T` transport structure required for propagation statements)
  - `paper4_deriving_local_reference_minus_i_from_admissible_mismatch_minimizing_selection.md` (defines transport residual `δ_T` and uses reference-mediated transport observables)
- Assumptions:
  - A1 (Well-typedness)
  - A10-style: composition is defined for the chain in the current residue context
- Prior lemmas: none

## Proof sketch
This lemma is a scaffold: it records the minimal transport axioms required for propagation identities. No further derivation is possible until `transport` and `∘` are explicitly defined in a concrete model (graph/ODE/PDE/etc.). ∎

## Status
draft

## Supersedes / Superseded-by

## Metadata (Migrated from LAW-003)
- **Law Conditions:**
  - orientation_pair_inputs_explicit
  - CSI_domain_explicit
  - transport_weighting_explicit
  - finite_flux_condition_explicit
  - noninvertibility_preserved
  - reconstruction_loss_preserved
  - composition_with_Pi_A_explicit
  - no_global_transport_closure_claim
- **Failure Modes:**
  - hidden_transport_invertibility
  - unbounded_CSI_summation
  - forced_global_transport_closure
  - orientation_locking
  - transport_flux_divergence
  - preimage_collapse
  - false_physical_transport_claim
  - operator_identity_overclaim

## Metadata (Migrated from LAW-016)
- **Law Conditions:**
  - orientation_array_dependency_explicit
  - channel_dependency_explicit
  - reconstruction_candidate_explicit
  - asymmetry_condition_explicit
  - loss_accumulation_condition_explicit
  - nonunique_prehistory_clause_explicit
  - irreversibility_projection_clause_explicit
  - no_entropy_equivalence_claim
- **Failure Modes:**
  - perfect_history_reconstruction_overclaim
  - unique_prehistory_overclaim
  - entropy_equivalence_leakage
  - hidden_absolute_time_ordering
  - lossless_continuation_assumption
  - primitive_memory_reintroduction
  - physics_claim_leakage
  - global_reversibility_overclaim

## Metadata (Migrated from LAW-023)
- **Law Conditions:**
  - orientation_array_dependency_explicit
  - local_reconstruction_operator_explicit
  - observable_subset_candidate_explicit
  - reconstruction_fidelity_candidate_explicit
  - ambiguity_region_candidate_explicit
  - hidden_topology_clause_explicit
  - bounded_observability_clause_explicit
  - non_observer_absolutism_clause_explicit
- **Failure Modes:**
  - global_observer_overclaim
  - complete_reconstruction_overclaim
  - observer_absolutism_leakage
  - hidden_topology_denial
  - lossless_observability_assumption
  - primitive_information_substance_reintroduction
  - consciousness_claim_leakage
  - physics_claim_leakage

