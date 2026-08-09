# Notebook 17 Design Reconstruction: Organization to Resolution to Distinction Density

## Provenance status

This document reconstructs the Notebook 17 design from the executed notebook and result archive. It was generated after execution and is not a pre-execution experiment specification. It does not remove the existing missing-distinct-specification blocker.

Campaign: `MPF_SIM_ORGANIZATION_RESOLUTION_CALCULUS_001`

Source notebook: `RT_Notebook_17_Organization_Resolution_Calculus.ipynb`

Input archive: `MPF_SIM_PROJECTION_DOF_MEANINGFUL_001_RESULTS.zip`

## Research question

Does organization remain a distinct operational construct when distinction density is resolved relative to explicit symmetry/reference conditions, and does projection preserve organization monotonically across the bounded organizational DoF domain?

## Hypotheses

The null hypothesis is that organization candidates are redundant with ordinary graph controls or collapse into the selected reference-resolved distinction density, with projection monotone in the bounded domain.

The bounded experimental hypothesis is that at least one organization candidate retains nonredundant signal after graph controls, reference choice changes resolved distinction density, and projection monotonicity is partial or counterexample-bearing.

## Operational construction

The notebook constructs four organization candidates from matched-null standardized structural deviations:

- `O_L1`: mean absolute standardized deviation,
- `O_L2`: root-mean-square standardized deviation,
- `O_MAX`: maximum absolute standardized deviation,
- `O_PCA1`: oriented first principal component.

It then resolves distinction density under four explicit reference families: uniform, depth, boundary, and closure. The notebook also tests incremental predictive contribution, residual independence, robustness relationships, and projection monotonicity.

## Controls and parameters

- Seed: `170017`.
- Five-fold cross-validation.
- 1,000 bootstrap repeats where applicable.
- Input: 527 organizations, 2,016 projection rows, and 15,810 perturbation rows from the Notebook 16 meaningful archive.
- Graph invariants remain controls; organization is not treated as a primitive.

## Expected and observed outputs

The result bundle contains candidate tables, reference-resolution tables, independence tests, robustness relationships, projection counterexamples, axiom tests, a decision record, and an execution manifest.

Observed archive disposition:

- best operational candidate: `O_MAX`,
- reference-dependent resolution observed,
- projection axiom partially supported,
- projection monotonicity rates between `0.8095` and `0.8274`, with counterexamples,
- primitive preservation not testable because both primitive classes were not represented,
- exact perturbation-level delta organization/density unavailable.

## Interpretation boundary

The archive supports only bounded operational observations within the supplied symbolic Notebook 16 domain. It does not establish a formal primitive, a unique organization metric, an implementation-independent calculus, universal projection monotonicity, primitive preservation, or external physical validity. The claim ceiling remains `C2_BOUNDED_NOTEBOOK_OUTPUT_WITH_LIMITATIONS` after governed induction.
