# Notebook 18 Domain Projection and Residue Review

## 1. Scope

This review covers the three Notebook 18 source notebooks housed under `departments/colab/notebook_designs/notebook_18_domain_projection_primitive_hierarchy/`, the companion `findings18.json`, and the executed archive `departments/colab/results/RT_Notebook_18_outputs.zip`.

The campaign is bounded to finite relational organizations of sizes 1 through 3, declared source domains `core`, `ordinal`, and `gradient`, target domains `ordinal`, `gradient`, and `temporal`, and the operational residue criteria recorded in the archive.

## 2. Directly observed/defined

- Source notebook hashes are preserved in the reconstruction manifest.
- Archive SHA-256: `ECE49AB849ADA10DB543738631F39A905288CA95BEE0E9969833F620671B1CAE`.
- The run manifest reports seed `180018`, `1,217,346` projection records, and `11,762` strong-admissibility records.
- Under strong admissibility, information residue has 1,672 zero-residue counterexamples (`0.14215`), structural residue has 2,608 (`0.22173`), and reference residue has 7,408 (`0.62982`).
- Under weak admissibility, information, structural, and reference criteria also have zero-residue counterexamples.
- Typed residue has no zero-residue cases in the tested records, but the archive explicitly notes that domain mismatch contributes directly to the typed criterion.
- The archive records information, structural, and reference hypotheses as `FALSIFIED_IN_TESTED_MODEL_CLASS`; typed residue is `NOT_FALSIFIED_IN_TESTED_MODEL_CLASS` with a definitional limitation.

## 3. Inferred inside the framework

Within the declared finite model class, domain difference alone does not force positive information, structural, or reference residue. The typed criterion remains positive because its operational definition includes domain mismatch, so it cannot independently establish a universal residue law.

## 4. External resemblance (analogy only)

The finite exhaustive/stratified enumeration resembles a bounded counterexample search over relational structures. That resemblance does not establish a theorem over unrestricted domains or identify the model with an external physical system.

## 5. What it does NOT prove

- It does not prove that every domain projection generates residue.
- It does not prove that the core primitive is unique outside the declared formal model.
- It does not establish a universal primitive hierarchy, external physical validity, or implementation-independent calculus.
- The surviving typed criterion is not independent evidence because domain mismatch is part of its definition.

## 6. Failure modes / uncertainty

- No distinct immutable pre-execution `experiment_spec.json` was supplied; the generated specification is explicitly post-execution reconstruction.
- Target blocks above the safety threshold use deterministic stratified enumeration rather than full target enumeration.
- The residue vector is operational and may not exhaust all possible residue notions.
- The archive includes companion findings and run manifests, but no separately registered pre-execution specification.
- Approved-tool replication remains pending.

## Evidence classification

`C2_BOUNDED_NOTEBOOK_OUTPUT_WITH_LIMITATIONS`

The three source notebooks are separately classified as `C1_NOTEBOOK_PROVENANCE`. No claim promotion above C2 is authorized.
