# CHAT_SEMANTIC_CAPTURE

- packet_id: `DISTINCTION_DENSITY_ENTROPY_CORRESPONDENCE_TEST_002`
- version: `1.0.0`
- captured_at: `2026-08-03`
- source_channel: `current_conversation_chat`
- input_class: `structured research execution instruction`
- canonicality: `NON_CANONICAL_CANDIDATE`
- preservation_status: `PRESERVED_BEFORE_EXECUTION`
- status: `AUTHORIZED_FOR_BOUNDED_EXECUTION`
- claim_ceiling: `C1`
- follows_failed_campaign: `DISTINCTION_DENSITY_STATISTICAL_MECHANICS_ENTROPY_001`

## Primary instruction

Test whether a non-circular, state-dependent distinction-density distribution can reproduce independently calculated entropy changes across ideal-gas, finite two-level, finite 2x2 Ising, and optional 3x3 Ising holdout regimes. Test generated distributions of admissible distinctions rather than raw support counts. Do not interpret distinction density as identical to entropy.

## Frozen definitions

- `d_i`: candidate locally admissible distinction associated with a primitive configuration or relation.
- `a_i(x)`: nonnegative structural accessibility from internal constraints, interactions, boundary conditions, and relational organization.
- `rho_D(i|x)`: frozen nonnegative generator output.
- `q_D(i|x) = rho_D(i|x) / sum_j rho_D(j|x)`; zero denominator is invalid.
- `S_D/k_B = -sum_i q_D(i|x) ln(q_D(i|x))`, with `0 ln 0 = 0`.
- `N_eff_D = exp(S_D/k_B)`.

The generator must be frozen before reference scoring and may not use canonical probabilities, Boltzmann probabilities, partition functions, density-matrix eigenvalues, reference entropy, direct microcanonical multiplicity, fitted reference coefficients, or target values.

## Candidate families

1. `DDG_GRAPH_CONSTRAINT_001`: density from local constraint compatibility, relational degree, interaction agreement, boundary accessibility, and orientation-sensitive organization.
2. `DDG_TRANSITION_ACCESSIBILITY_001`: density from admissible primitive transitions and preregistered structural transition weights; weights may not encode canonical probabilities.

At least two independently motivated families must be implemented before held-out results are exposed. Selection is deterministic: leakage pass, invariance pass, beat uniform/support controls on at least two construction regimes, then lowest normalized construction error.

## Reference regimes and separation

- `IDEAL_GAS`: construction particle counts `[1,2,4]`, volumes `[1.0,1.5,2.0,3.0]`; holdout counts `[3,5]`, volumes `[1.25,2.5,4.0,8.0]`; include forward, reverse, and multistep volume paths. Support-count scaling is a named baseline only.
- `TWO_LEVEL_SYSTEM`: gap `1.0`; construction temperatures `[0.4,0.8,1.5,3.0]`; holdout temperatures `[0.5,1.0,2.0,4.0]`, gaps `[0.5,1.5,2.0]`.
- `ISING_2X2`: construction temperatures `[0.6,1.2,2.5,5.0]`, couplings `[0.5,1.0]`, fields `[-0.5,0,0.5]`; holdout temperatures `[0.5,1,2,4]`, couplings `[0.75,1.25]`, fields `[-0.25,0.25]`.
- `ISING_3X3_HOLDOUT_ONLY`: temperatures `[0.75,1.5,3.0]`, coupling `1.0`, field `0.0`, if exact enumeration is feasible; no post-exposure generator changes.

Reference modules must be separate from candidate modules and independently implemented.

## Controls, audits, and metrics

Required controls: uniform, support-count, fixed seeded random, statewise seeded random, permutation, energy-rank-only, and Boltzmann oracle (oracle only). Required audits: source hashes, candidate input/output records, import separation, forbidden-term static audit, runtime leakage audit, normalization, permutation invariance, repeatability, interaction sensitivity, and state identity.

Required metrics: absolute and normalized transition error, sign agreement, rank correlation, path error, reverse error, permutation error, repeatability error, and candidate advantage over controls. Key thresholds include permutation/repeatability `<=1e-12`, path/reverse `<=1e-10`, minimum sign agreement `0.9`, minimum rank correlation `0.9`, maximum median normalized error `0.25`, maximum regime normalized error `0.5`, and at least three successful primary regimes.

## Required outputs and stop conditions

Write the campaign bundle under `results/distinction_density_entropy_002/`, including frozen specification, source hashes, candidate inputs/outputs, construction and holdout results, selected candidate, controls, leakage audit, invariance/path tests, independent verification, falsification assessment, and research report.

Stop if the generator is incomplete, forbidden reference data is used, construction/holdout separation is absent, hashes are missing, normalization fails, or the primary candidate changes after holdout exposure. Final statuses include `SUPPORTED_FOR_EXECUTED_BOUNDS`, `PARTIALLY_SUPPORTED_REGIME_LIMITED`, `FALSIFIED_FOR_EXECUTED_GENERATOR`, `INVALID_REFERENCE_LEAKAGE`, `CIRCULARLY_UNDERDETERMINED`, and `EXECUTION_BLOCKED`.

## Capture limitation

This is a semantic preservation of the received structured packet for intake routing. The packet remains provisional and non-canonical; preservation does not promote its claims or authorize changes to authoritative registries.
