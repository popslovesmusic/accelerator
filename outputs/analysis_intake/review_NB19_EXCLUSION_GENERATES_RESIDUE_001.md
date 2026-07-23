# Notebook 19 Result Review

## Scope

Review of `RT_Notebook_19_outputs.zip` and the executed Notebook 19 source for bounded exclusion/residue testing.

## Directly observed/defined

- Archive SHA-256: `CB4B682FAB3D88DC02224AAFCA48D5E96A9B65EC534665EAA705FA742905D209`.
- Internal manifest is present; seed `190019`, 1,217,346 total records, and 11,762 strong records.
- Strong information criterion: sufficiency and necessity falsified; 162 exclusion-without-residue and 382 residue-without-exclusion cases.
- Strong structural criterion: sufficiency and necessity falsified; 1,098 exclusion-without-residue and 382 residue-without-exclusion cases.
- Strong total criterion: sufficiency not falsified, necessity falsified by 706 residue-without-exclusion cases; the biconditional is falsified.

## Inferred inside framework

Within this finite operational model, exclusion and residue are correlated in tested projections but are not equivalent under the information or structural criteria. Total residue supports only a one-direction bounded result.

## External resemblance (analogy only)

The counterexample workflow resembles finite model checking and hypothesis falsification. That resemblance does not establish identity with an external causal or mathematical theory.

## What it does not prove

It does not establish a universal exclusion law, primitive causation, implementation-independent validity, external physical validity, or C5/C6 evidence.

## Failure modes / uncertainty

The model is finite and bounded; target blocks may use deterministic stratification; exclusion and residue are operational definitions; no immutable pre-execution specification was supplied; and approved-tool replication is pending.
