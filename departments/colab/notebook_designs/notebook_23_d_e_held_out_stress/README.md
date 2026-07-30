# Notebook 23: Held-Out D/E Stress Test

Status: pre-execution design. No execution or result evidence is implied.

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

The test does not promote `OBL-D-001D`, `OBL-D-001E`, the D package, or any external claim above its governed ceiling.
