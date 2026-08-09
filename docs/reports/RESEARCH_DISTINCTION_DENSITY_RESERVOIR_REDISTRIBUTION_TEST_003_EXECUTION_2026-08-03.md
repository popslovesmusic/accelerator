# RESEARCH REPORT: Reservoir-Conditioned Distinction-Density Redistribution Campaign 003

## 0. Metadata
```json
{
  "packet_id": "DISTINCTION_DENSITY_RESERVOIR_REDISTRIBUTION_TEST_003",
  "campaign_id": "distinction_density_reservoir_redistribution_003",
  "status": "FALSIFIED_FOR_EXECUTED_REDISTRIBUTION_GENERATOR",
  "claim_ceiling": "C1",
  "selected_candidate": "RDC_CAPACITY_TRANSPORT_001",
  "H2": "BLOCKED_H1_FAILURE",
  "H3": "PASS",
  "H4": "PASS",
  "independent_verification": "PASS"
}
```

## 1. Predecessor constraints

Campaigns 001 and 002 remain preserved as failed results. Their generators were not revised or reused as primary candidates. This campaign kept total capacity, relative shape, redistribution, coupling, and `entropy_app` separate.

## 2. Claim tested

The primary claim was that a frozen reservoir-conditioned redistribution measure predicts the ordinal direction of independently calculated reference entropy change. A secondary magnitude projection was permitted only after H1 was evaluated and frozen. The zero-DOF closure claim and coupling-sensitivity claim were tested separately.

## 3. Framework proposition and candidate definitions

The executed objects were:

- `C_D`: total distinction capacity;
- `q_D`: relative shape descriptor;
- `R_D`: signed redistribution measure;
- `K_r`: reservoir coupling descriptor;
- `entropy_app`: observational output, never a dynamics input.

Three new families were implemented:

1. `RDC_CAPACITY_TRANSPORT_001`;
2. `RDC_BOUNDARY_ACCESSIBILITY_001`;
3. `RDC_ADMISSIBLE_TRANSITION_FLOW_001`.

The deterministic construction rule selected `RDC_CAPACITY_TRANSPORT_001` with macro construction balanced accuracy `0.48148148`.

## 4. Direct observations

Candidate fields were generated and serialized before reference-module execution. Static and runtime leakage audits passed. All required fields were nonnegative and normalized only for `q_D`; total capacity was retained for scoring.

The selected candidate’s holdout ordinal scores were:

| Regime | Balanced accuracy | Sign agreement | Abstention |
|---|---:|---:|---:|
| Ideal-gas boundary | `0.50` | `1.00` | `0.00` |
| Two-level reservoir | `0.4722` | `0.9444` | `0.00` |
| Ising reservoir | `0.50` | `1.00` | `0.00` |

The high sign-agreement values are not sufficient for the preregistered criterion because the selected candidate predominantly predicted the positive class; balanced accuracy exposed that failure.

## 5. Closed-domain zero-DOF test

With `K_r=0`, intervening on `entropy_app` alone changed the next-condition prediction by `0.0`. The candidate update did not read `entropy_app` as a dynamics input.

H3 result: **PASS**.

## 6. Reservoir-draw and coupling test

Changing `K_r` from zero to one changed `R_D` for all three candidate families. The coupling-sensitivity test therefore passed within this bounded operationalization.

H4 result: **PASS**. This establishes sensitivity of the candidate measure to the declared coupling input, not physical reservoir causation.

## 7. Construction ordinal results and selected candidate

The candidate selection was performed on construction conditions only. Holdout values were not used to select the primary family. The selected family’s construction score exceeded the other two families under the frozen macro-balanced-accuracy rule, but the score remained below the packet’s acceptance threshold.

## 8. Held-out ordinal results

H1 failed because none of the three primary regimes reached balanced accuracy `>=0.75`. H2 was blocked and no magnitude projection was fitted or used to rescue the H1 failure.

The 3×3 topology transfer was not accepted as a successful generalization result because H1 had already failed; its output remains diagnostic only.

## 9. Control comparisons

Scored controls included no-redistribution, support-count, normalized-Shannon, capacity-only, energy-rank, temperature-sign, majority-sign, fixed random, statewise random, permutation, and oracle-only reference controls.

The selected candidate did not satisfy the required control-separation and primary-regime criteria. The oracle remained classification `ORACLE_ONLY_NOT_CANDIDATE`.

## 10. Leakage, structural, and path audits

- Static candidate audit: PASS.
- Runtime input audit: PASS.
- Candidate output hash locking: PASS.
- Permutation test: PASS.
- Path/reversal test: PASS.
- Closure intervention: PASS.
- Reservoir coupling sensitivity: PASS.

These are execution-integrity findings, not evidence of physical correspondence.

## 11. Independent verification

The independent verifier recomputed `R_D` from serialized before/after density fields without importing the campaign runner. It reproduced all `102` selected holdout redistribution rows and verified the recorded H1 result.

Independent verification: **PASS**.

## 12. Falsification assessment

| Vector | Result | Finding |
|---|---|---|
| FV-1 ordinal failure | FAIL | H1 balanced-accuracy criteria failed. |
| FV-2 control failure | FAIL | Required control separation was not demonstrated. |
| FV-3 zero-DOF failure | PASS | `entropy_app` intervention had zero effect at `K_r=0`. |
| FV-4 reservoir failure | PASS | Candidate measures changed with `K_r`. |
| FV-5 leakage | PASS | No forbidden reference input detected. |
| FV-6 normalization collapse | PASS | Capacity was retained separately from `q_D`. |
| FV-7 topology failure | NOT_ACCEPTED | H1 failure blocks promotion of topology transfer. |
| FV-8 magnitude failure | BLOCKED | H2 was not evaluated after H1 failure. |
| FV-9 circular equivalence | NOT ESTABLISHED | No circular equivalence was claimed. |
| FV-10 temperature shortcut | NOT PROMOTED | H1 already failed before any rescue interpretation. |

Final status: `FALSIFIED_FOR_EXECUTED_REDISTRIBUTION_GENERATOR`.

## 13. Framework-limited inference

Within the executed bounds, the selected reservoir-conditioned redistribution family did not meet the preregistered ordinal acceptance criteria, despite passing closure and coupling-sensitivity checks. The result identifies a mismatch between structural sensitivity and reference entropy-direction classification; it does not establish that reservoir-conditioned distinction redistribution is impossible in every formulation.

## 14. External analogy only

The reservoir and entropy terms are model labels used in a bounded comparison with finite reference calculations. The execution does not validate a thermodynamic reservoir, physical entropy, or causal mechanism in external reality.

## 15. What the execution does not prove

It does not prove that distinction density is entropy, that entropy is caused by reservoir redistribution, that the RT framework reproduces thermodynamics, or that H3/H4 passing establishes physical closure or coupling.

## 16. Next action

Preserve DDG-003 as falsified for the executed generator. Do not revise candidates after holdout exposure. Any follow-up requires a new frozen packet with a better-balanced transition design and an independently justified redistribution law; H2 must remain blocked unless a future H1 passes.

## Output index

- `results/distinction_density_reservoir_redistribution_003/campaign_results.json`
- `results/distinction_density_reservoir_redistribution_003/falsification_assessment.json`
- `results/distinction_density_reservoir_redistribution_003/independent_verification.json`
- `results/distinction_density_reservoir_redistribution_003/closed_domain_zero_dof_test.json`
- `results/distinction_density_reservoir_redistribution_003/reservoir_draw_test.json`
