# RESEARCH REPORT: DDG-002 State-Dependent Distinction-Density Campaign

## 0. Metadata
```json
{
  "packet_id": "DISTINCTION_DENSITY_ENTROPY_CORRESPONDENCE_TEST_002",
  "campaign_id": "distinction_density_entropy_002",
  "status": "FALSIFIED_FOR_EXECUTED_GENERATOR",
  "claim_ceiling": "C1",
  "selected_candidate": "DDG_GRAPH_CONSTRAINT_001",
  "independent_verification": "PASS",
  "recoverable_output_root": "results/distinction_density_entropy_002"
}
```

## 1. Claim tested

The packet hypothesis was: a frozen, non-circular, state-dependent distinction-density generator can reproduce the direction and bounded magnitude of independently calculated entropy changes across ideal-gas, two-level, and finite Ising regimes.

The result is specific to the two executed candidate families and the selected generator. It is not a test of every possible RT density formulation.

## 2. Generator definitions

Two candidate families were implemented before reference import:

- `DDG_GRAPH_CONSTRAINT_001`: local compatibility, relational participation, boundary accessibility, and orientation terms.
- `DDG_TRANSITION_ACCESSIBILITY_001`: structural transition accessibility based on local spin/configuration relations and fixed transition weights.

Both produced nonnegative, normalizable density fields. Candidate outputs were serialized and hash-locked before the reference module was imported.

## 3. Direct observations

The deterministic construction selection rule chose `DDG_GRAPH_CONSTRAINT_001`, with aggregate construction median normalized error `2.9990410573`, versus `3.0050959660` for `DDG_TRANSITION_ACCESSIBILITY_001`.

The leakage audit passed: no forbidden reference quantity was detected in candidate source or runtime inputs.

## 4. Construction results

The selected candidate was chosen using construction data only. No holdout values were used for selection, and no candidate was edited after holdout exposure.

The selection outcome did not meet the packet’s stronger construction-control requirement; therefore the campaign cannot be promoted as a successful construction-stage correspondence.

## 5. Held-out results

| Regime | Median normalized error | Sign agreement | Maximum absolute error |
|---|---:|---:|---:|
| Ideal gas | `1.0027500361` | `0.00` | `3.4793894232` |
| Two-level system | `1.0019232585` | `0.50` | `0.2837553814` |
| 2×2 Ising | `1.0002674897` | `0.00` | `1.25441731599` |
| 3×3 Ising holdout | `0.9999904600` | `1.00` | `2.42856854658` |

The primary cross-regime acceptance criteria were not met. In particular, the selected candidate did not reach the required sign agreement or error bounds in the primary regimes.

## 6. Control comparisons

The scored controls included uniform, support-count, fixed seeded random, statewise seeded random, permutation, energy-rank-only, and Boltzmann oracle controls. The uniform, support-count, fixed-random, and energy-rank controls produced median normalized errors near `1.0` in the fixed-support regimes. The permutation control preserved the candidate entropy, as required by label invariance. The Boltzmann oracle scored as an oracle only and was not treated as a candidate.

The selected candidate did not demonstrate the required advantage over the non-oracle controls.

## 7. Leakage and structural audits

- Candidate source static audit: PASS.
- Candidate outputs hash-locked before reference import: PASS.
- Reference module imported after candidate serialization: PASS.
- Forbidden runtime inputs: none detected.
- Density nonnegativity and normalization: PASS.
- Path and reverse checks: PASS for the implemented trajectories.

These checks validate execution hygiene and internal bookkeeping, not physical correctness.

## 8. Independent verification

The independent Python verifier did not import the campaign runner. It recomputed reference entropies independently and recomputed candidate entropy readouts from serialized density outputs.

It reproduced every recorded holdout maximum-error and sign-agreement result for all four evaluated regimes. Independent verification status: **PASS**.

## 9. Falsification assessment

| Vector | Result | Finding |
|---|---|---|
| FV-1 cross-regime | FAIL | Primary candidate missed cross-regime acceptance. |
| FV-2 control separation | FAIL | Required advantage over simple controls was not demonstrated. |
| FV-3 reference leakage | PASS | No forbidden reference input detected. |
| FV-4 permutation | PASS | Label permutation did not alter the entropy readout. |
| FV-5 path/reversal | PASS | Implemented path and reversal invariants passed. |
| FV-6 topology transfer | FAIL | 3×3 did not meet magnitude criteria despite sign agreement. |
| FV-7 circular equivalence | NOT ESTABLISHED | No oracle equivalence was claimed; further algebraic analysis remains open. |

Final status: `FALSIFIED_FOR_EXECUTED_GENERATOR`.

## 10. Framework-limited inference

Within the executed bounds, the two frozen structural families did not reproduce statistical-mechanics entropy changes with the required magnitude and cross-regime behavior. The result identifies insufficient state-sensitive structure in these candidates; it does not show that a richer distinction-density generator is impossible.

## 11. External analogy only

The benchmark comparison is a mathematical correspondence test against finite statistical-mechanics reference calculations. It is not evidence that distinction density is a physical entropy field or that the RT framework explains thermodynamic systems.

## 12. What the execution does not prove

It does not prove identity or non-identity between distinction density and entropy in general, validate thermodynamics externally, validate the RT ontology, or justify a physical interpretation of the candidate inputs. It also does not promote the packet above C1.

## 13. Failure modes and uncertainty

- The candidate feature functions were bounded operationalizations, not derived laws.
- The ideal-gas and finite-state representations remain sensitive to how distinctions are enumerated.
- The scoring package records the required controls, but the campaign does not establish a universal control ranking.
- The 3×3 exact holdout was computationally feasible and failed the magnitude criterion.
- Further candidates must be frozen and audited before any new holdout exposure.

## 14. Next action

Do not revise DDG-002 after holdout failure. Preserve the outputs and classify the executed generator as falsified. Any follow-up must define a new candidate family with an independent justification for state-dependent accessibility, rerun construction selection, and repeat the leakage and holdout protocol from a new packet or authorized revision.

## Output index

- `results/distinction_density_entropy_002/campaign_results.json`
- `results/distinction_density_entropy_002/falsification_assessment.json`
- `results/distinction_density_entropy_002/independent_verification.json`
- `results/distinction_density_entropy_002/control_results.json`
- `results/distinction_density_entropy_002/source_hashes.json`
