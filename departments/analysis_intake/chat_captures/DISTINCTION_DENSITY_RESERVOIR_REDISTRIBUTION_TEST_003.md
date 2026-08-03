# CHAT_SEMANTIC_CAPTURE

- packet_id: `DISTINCTION_DENSITY_RESERVOIR_REDISTRIBUTION_TEST_003`
- version: `1.0.0`
- captured_at: `2026-08-03`
- source_channel: `current_conversation_chat`
- input_class: `structured research execution instruction`
- canonicality: `NON_CANONICAL_CANDIDATE`
- preservation_status: `PRESERVED_BEFORE_EXECUTION`
- status: `AUTHORIZED_FOR_BOUNDED_EXECUTION`
- campaign_id: `distinction_density_reservoir_redistribution_003`
- claim_ceiling: `C1`
- recoverable_output_root: `results/distinction_density_reservoir_redistribution_003`

## Predecessor constraints

The packet follows failed campaigns `DISTINCTION_DENSITY_STATISTICAL_MECHANICS_ENTROPY_001` and `DISTINCTION_DENSITY_ENTROPY_CORRESPONDENCE_TEST_002`. Their failed generators and outputs must remain immutable. This campaign must not model entropy as automatically identical to the Shannon entropy of a normalized distinction field.

## Research questions and hypotheses

Primary question: whether reservoir-conditioned redistribution of distinction density predicts the ordinal direction of independently calculated entropy change without defining entropy as a normalized-density Shannon readout.

- `H1_ORDINAL_REDISTRIBUTION`: sign of frozen redistribution measure matches reference entropy-change sign under reservoir coupling.
- `H2_MAGNITUDE_PROJECTION`: after H1 is frozen, a separate projection predicts bounded magnitude on holdout conditions; H2 may not rescue H1 failure.
- `H3_CLOSURE_ZERO_DOF`: with `K_r=0`, changing `entropy_app` alone cannot change the next system condition.
- `H4_COUPLING_SENSITIVITY`: changing reservoir coupling changes candidate redistribution when accessibility differs.

## Separate quantities

- `C_D`: total distinction capacity, `sum_i rho_D(i|x)`.
- `q_D`: relative distribution, `rho_D/C_D`; shape only, not a replacement for capacity.
- `R_D`: transition-specific redistribution containing capacity, topology, accessibility, and coupling-conditioned change.
- `K_r`: reservoir coupling; zero means closure for the tested channel.
- `entropy_app`: derived observational projection, never a candidate-generator input.

The candidate must not collapse capacity, distribution, redistribution, coupling, and entropy projection into one quantity.

## Candidate families and reference separation

Implement at least two new redistribution families, not the failed DDG-002 generators:

1. `RDC_CAPACITY_TRANSPORT_001`: signed capacity change plus topology-aware relocation and accessibility change.
2. `RDC_BOUNDARY_ACCESSIBILITY_001`: boundary accessibility, capacity, organization, and `K_r` changes.
3. `RDC_ADMISSIBLE_TRANSITION_FLOW_001`: change in admissible transition-flow structure with frozen structural weights.

Candidate generation must not use canonical probabilities, Boltzmann factors, partition functions, reference entropy, free energy, heat capacity, oracle probabilities, or reference formulas as candidate answers. Candidate outputs are generated, serialized, and hash-locked before reference scoring.

## Regimes and tests

- Two-level reservoir: construction gaps `[0.5,1.0,1.5]`, temperatures `[0.4,0.8,1.5,3.0]`, couplings `[0.25,0.5,1.0]`; holdout gaps `[0.75,1.25,2.0]`, temperatures `[0.5,1.0,2.0,4.0]`, couplings `[0.4,0.75]`.
- Ising reservoir: construction 2x2/2x3 periodic; holdout 3x3 periodic/open; temperature, coupling, field, and reservoir-coupling grids as supplied in the packet.
- Ideal-gas boundary: construction counts `[1,2,4]`, volumes `[1.0,1.5,2.0,3.0]`, boundary accessibility `[0.25,0.5,1.0]`; holdout counts `[3,5]`, volumes `[1.25,2.5,4.0,8.0]`, accessibility `[0.4,0.75]`.

Required tests include temperature/coupling changes, coupling removal, field reversal, topology transfer, path/reverse transitions, closed-domain `K_r=0`, and reservoir draws.

## Controls and acceptance

Controls: no redistribution, support count, normalized Shannon, capacity-only, energy rank, temperature-sign, majority-sign, fixed/statewise random, permutation, and oracle-only reference. Required structural tolerances include permutation `<=1e-12`, repeatability `<=1e-12`, path/reverse `<=1e-10`, and closure intervention `<=1e-12`. H1 requires balanced accuracy `>=0.75`, macro-F1 `>=0.70`, sign agreement `>=0.80`, abstention `<=0.20`, three successful primary regimes, and control separation.

H2 is evaluated only after H1 outputs are frozen. H3 requires zero causal effect from intervening on `entropy_app` at `K_r=0`. H4 requires coupling sensitivity above fixed/no-redistribution controls.

## Required outputs and final-status options

The campaign must produce the packet’s full output bundle under `results/distinction_density_reservoir_redistribution_003/`, including frozen specifications, structural outputs, ordinal and magnitude results, closure and reservoir tests, controls, leakage audits, independent verification, falsification assessment, and report.

Final status must remain one of the packet’s bounded options, including `SUPPORTED_FOR_EXECUTED_BOUNDS`, `ORDINAL_CORRESPONDENCE_ONLY`, `FALSIFIED_FOR_EXECUTED_REDISTRIBUTION_GENERATOR`, `REJECT_ZERO_DOF_ENTROPY_PROPOSITION_FOR_EXECUTED_MODEL`, `REJECT_RESERVOIR_DRAW_MECHANISM_FOR_EXECUTED_MODEL`, `INVALID_REFERENCE_LEAKAGE`, `INVALID_OPERATIONALIZATION`, or `EXECUTION_BLOCKED`.

## Capture limitation

This is a semantic preservation of the received structured packet for governed routing. The packet remains provisional and non-canonical; preservation does not promote claims or alter authoritative registries.
