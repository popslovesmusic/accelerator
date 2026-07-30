# Notebook 23: Held-Out D/E Stress Test

Status: executed archive attached; governed induction and integrity review remain pending.

This Colab-only test evaluates whether the bounded P127/P128 behavior survives held-out contexts and source-relation cases that were not used in the existing finite fixtures. It is designed to find counterexamples, not to confirm a theorem.

The notebook must use only the frozen predicates and typed fields declared in `experiment_spec.json`. It must not import external runners or unapproved simulation tools.

Claim ceiling:

- Before execution: `C1_EXPERIMENT_SPECIFICATION`.
- After recoverable, manifest-backed execution and governed review: at most `C2_LIMITATION_OR_NEGATIVE_RESULT`.

Required before execution:

- Freeze `experiment_spec.json` and preserve its SHA-256.
- Preserve the notebook hash.
- Execute in Colab or an approved reconstruction environment.
- Write outputs under `departments/colab/results/MPF_SIM_D_E_HELD_OUT_STRESS_001/`.
- Produce a manifest, per-row hashes, and an explicit falsification report.
- Bind any result archive through the induction queue and Colab archive registry before interpretation.

Post-run documentation is provided by `RT_Notebook_23_D_E_Held_Out_Stress_Analysis.ipynb`. With no archive, it records `BLOCKED_NO_EXECUTION_ARCHIVE`; with a complete archive, it emits bounded counts, replay agreement, and falsification findings for governed review.

The executed source notebook is now the canonical `RT_Notebook_23_D_E_Held_Out_Stress.ipynb`. The original two-cell design skeleton is retained as `RT_Notebook_23_D_E_Held_Out_Stress_DESIGN_SPECIFICATION.ipynb`. The attached archive is `departments/colab/results/MPF_SIM_D_E_HELD_OUT_STRESS_001_RESULTS.zip`.

The test does not promote `OBL-D-001D`, `OBL-D-001E`, the D package, or any external claim above its governed ceiling.
