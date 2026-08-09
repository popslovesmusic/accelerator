# Notebook 20 Result Review

## Scope

Review of `RT_Notebook_20_outputs.zip` and the executed Notebook 20 source for distinction conservation and exclusion/residue coupling.

## Directly observed/defined

- Archive SHA-256: `6E009048752D8745398C1C6939B4A02BE2F8E5B7826F4759FE5A3BED8ED73B85`.
- Internal manifest is present; seed `200020`, 4,813,425 projections, and 25,478,208 distinction instances.
- Conservation failures: `0`; conservation verdict: `NOT_FALSIFIED_IN_TESTED_MODEL_CLASS`.
- Strong-form matched-exclusion counterexamples: `478`; strong-form verdict: `FALSIFIED_IN_TESTED_MODEL_CLASS`.
- Best reported linear model has `r_squared` approximately `0.1183`, so excluded-count-only prediction is weak in the reported fits.

## Inferred inside framework

Within the bounded operational model, source distinctions were classified exactly once as preserved or excluded, while identical exclusion signatures did not determine a unique residue value.

## External resemblance (analogy only)

The campaign resembles finite partition checking and counterexample-based model analysis. That resemblance is not identity with a general conservation law.

## What it does not prove

It does not establish universal distinction conservation, a causal residue law, implementation-independent validity, or external physical validity.

## Failure modes / uncertainty

The model is finite; distinctions are pairwise state distinctions; residue is operationalized; conservation may partly reflect the partition definition; matched-signature testing depends on sampled blocks; deterministic stratification is used in some blocks; no immutable pre-execution specification was supplied; and approved-tool replication is pending.
