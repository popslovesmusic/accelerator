# RESEARCH REPORT: Distinction-Density Entropy Correspondence Execution

## 0. Metadata
```json
{
  "claim_id": "DISTINCTION_DENSITY_STATISTICAL_MECHANICS_ENTROPY_001",
  "status": "FALSIFIED_FOR_MINIMAL_OPERATIONALIZATION",
  "classification": "bounded_campaign_result",
  "charter_classification": "provisional",
  "claim_ceiling": "C1",
  "campaign_id": "distinction_density_entropy_001",
  "recoverable_output_root": "results/distinction_density_entropy_001"
}
```

## 1. Abstract

The preregistered minimal non-circular distinction-density operationalization was executed against ideal-gas, finite two-level, and finite 2×2 Ising reference calculations. It reproduced the ideal-gas volume-change entropy increments to floating-point precision, but failed the cross-regime hypothesis because the two-level and Ising density proxies were temperature-independent uniform fields. Their predicted entropy changes were zero while the independent statistical-mechanics references changed with temperature.

The leakage audit and path/reversal consistency checks passed. Uniform-density and permutation controls were not separated from the candidate. This result falsifies H1 for the executed operationalization; it does not show that every possible mathematically defined distinction-density distribution must fail.

## 2. Core Principle Context

The governing framework expression is `(ℰ≠0) ⇔_R δ(ℰ>0)`, treated here as a source of organizational structure rather than a physical entropy equation. The executed mapping was a candidate downstream projection:

```text
density field → normalized weights → Shannon-form entropy readout
```

The execution therefore tests a specific operationalization, not the entire RT framework.

## 3. Directly observed and defined

The frozen candidate generator was:

- ideal gas: 16 uniform admissible cells per volume unit;
- two-level system: two uniform state weights independent of temperature;
- 2×2 Ising system: sixteen uniform state weights independent of temperature or field.

The entropy readout was `S_D/k_B = -Σ q_D ln(q_D)`, with `q_D` formed by normalizing the candidate density field. The reference values were independently computed from the ideal-gas formula, finite two-level canonical weights, and exact enumeration of the 2×2 Ising states.

## 4. Experimental setup

The campaign used predeclared state sequences:

- ideal-gas volumes `1, 2, 4, 8`;
- two-level temperatures `0.5, 1, 2, 4` with unit energy gap;
- 2×2 Ising temperatures `0.5, 1, 2, 4`, zero field, unit coupling.

No regime-specific fit, entropy target, partition function, statistical-mechanics probability, or reference entropy value was supplied to the candidate generator. Because the candidate had no fitted parameters, all declared evaluation states were scored without tuning; a separate construction subset was not needed for this fixed operationalization, but the full holdout campaign remains a later requirement for any richer generator.

## 5. Results

| Regime | Maximum absolute error in `ΔS/k_B` | Sign agreement | Path error | Reverse error |
|---|---:|---|---:|---:|
| Ideal gas | `3.33e-16` | true | `0` | `0` |
| Two-level | `0.32006144` | false | `0` | `0` |
| 2×2 Ising | `1.92999063` | false | `0` | `0` |

Reference entropy changes for the two-level and Ising systems were positive across the tested temperature increases, while the uniform candidate fields produced zero changes. The complete machine-readable result is in `results/distinction_density_entropy_001/campaign_results.json`.

## 6. Falsification assessment

| Vector | Result | Meaning |
|---|---|---|
| FV-1 cross-regime agreement | FAIL | Two-level and Ising sign/magnitude criteria failed. |
| FV-2 path/reversal consistency | PASS | The candidate changes were internally additive and reversible for these paths. |
| FV-3 reference leakage | PASS | No forbidden reference quantities were supplied to the candidate generator. |
| FV-4 control separation | FAIL | Uniform and permutation controls were not separated from the candidate. |

The primary H1 criterion therefore failed.

## 7. Inferred inside the framework

The executed result indicates that the current minimal density definition does not contain enough temperature- or interaction-sensitive structure to reproduce the tested canonical entropy changes across regimes. The ideal-gas match arose from the declared volume-dependent support size, while the finite-state proxies remained uniform and therefore insensitive to thermodynamic state changes.

This is a bounded model diagnosis, not a proof of impossibility.

## 8. External resemblance and analogy only

The ideal-gas match resembles the familiar logarithmic volume dependence because the candidate support count was made proportional to volume. That resemblance is not independent evidence of a physical derivation; it identifies a structural input that already carries the relevant volume scaling.

## 9. What this does not prove

This execution does not prove that distinction density is thermodynamic entropy, that statistical mechanics is reproduced by RT, that the RT framework lacks a successful density generator, or that any physical system is explained. It also does not validate the sphere, hexahedron, reservoir, or MTO/OTM proposals.

## 10. Failure modes and uncertainty

- The operationalization was intentionally minimal and may omit the unresolved state-dependent density law.
- The ideal-gas support rule is structurally informative but may be considered an imported volume-to-capacity assumption.
- The finite two-level and Ising candidates were deliberately uniform; their failure diagnoses missing structure but does not select the missing structure.
- A future candidate must be frozen before reference scoring and must not encode Boltzmann weights under a different name.
- A future campaign must add a genuine construction/holdout split for any fitted or learned density generator.

## 11. Next action

Do not promote H1. Define and justify a state-dependent distinction-density generator independently of `p_SM`, `Z`, `Ω`, and `S_SM`; then rerun the leakage audit, controls, and a true construction/holdout campaign. If the generator cannot be specified without importing the reference distribution, record the bridge as circularly underdetermined.

## Status Footer

- **Execution script:** `scripts/research/run_distinction_density_entropy_001.py`
- **Recoverable outputs:** `results/distinction_density_entropy_001/`
- **Design report:** `docs/reports/RESEARCH_DISTINCTION_DENSITY_STATISTICAL_MECHANICS_ENTROPY_TEST_DESIGN_2026-08-03.md`
