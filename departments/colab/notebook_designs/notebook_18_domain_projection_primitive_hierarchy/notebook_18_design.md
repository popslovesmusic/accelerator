# Notebook 18 Design: Domain Projection and Primitive Hierarchy

## Provenance status

This document reconstructs the Notebook 18 design from three source notebooks and the executed result archive. It was generated after execution and is not a pre-execution experiment specification. It does not remove the missing-distinct-specification blocker.

## Source bundle

- `RT_Notebook_18_Domain_Projection_and_Primitive_Hierarchy.ipynb`: initial domain and primitive-hierarchy scaffold.
- `RT_Notebook_18_Domain_Projection_and_Primitive_Hierarchy_COMPLETE.ipynb`: completed domain/projection prototype and findings scaffold.
- `RT_Notebook_18_Every_Domain_Projection_Generates_Residue.ipynb`: falsification campaign that produced the executed archive.

## Research questions

1. How can a single primitive relational condition remain invariant while richer structures become admissible as domain degrees of freedom increase?
2. Does every genuine projection between distinct domains necessarily generate residue?

## Model

A finite relational organization is represented by members, binary orientation labels, undirected relation edges, an optional reference member, and a declared domain type. Projections are total deterministic maps between source and target organizations.

Two admissibility classes are evaluated:

- `weak`: total cross-domain maps;
- `strong`: maps satisfying coverage, reference, orientation, and relation-preservation constraints.

Residue is evaluated as a vector rather than a single preferred quantity: information, structural, reference, inverse, and typed-domain components are tracked. The universal hypothesis is tested separately for information, structural, reference, and typed criteria.

## Bounded parameters

- Source domains: `core`, `ordinal`, `gradient`.
- Target domains: `ordinal`, `gradient`, `temporal`.
- Source and target sizes: `1..3`.
- Seed: `180018`.
- Target safety threshold: `500`, with deterministic stratification above the threshold.
- Weak records: `1,217,346`.
- Strong records: `11,762`.

## Direct result disposition

In the tested finite model class, information, structural, and reference residue hypotheses are falsified by zero-residue counterexamples under both weak and strong admissibility. Typed residue is not falsified, but the typed criterion includes domain mismatch by definition and therefore is not independent evidence for universal residue generation.

## Interpretation boundary

The archive supports bounded falsification and operational model analysis only. It does not prove a universal residue law, a primitive hierarchy outside the declared model, an external physical identity, or a theorem over unrestricted domains. The claim ceiling remains `C2_BOUNDED_NOTEBOOK_OUTPUT_WITH_LIMITATIONS` after governed induction.
