# Notebook 20 Design: Distinction Conservation and Exclusion Dynamics

## Scope

Notebook 20 tests two separate propositions in a finite relational organization model: whether source distinctions are partitioned exactly once into preserved or excluded distinctions, and whether the excluded distinction set determines residue.

## Operational model

Distinctions are pairwise state distinctions with label, relation-profile, and reference components. Projection classifies each source distinction as preserved or excluded. Residue is measured through operational relation, inverse, reference, and total residue components.

## Bounded execution

The archive reports seed `200020`, 4,813,425 projection records, and 25,478,208 distinction instances. Domains are binary, ternary, and relational; source sizes are 2 through 4 and target sizes are 1 through 4. Blocks may be exhaustive or deterministic stratified subsets.

## Direct result disposition

No conservation failures were observed in the tested model class. The strong residue-determination form was falsified: 478 matched exclusion signatures produced differing residue values. The best linear fits have low explanatory strength, with the highest reported `r_squared` equal to approximately `0.1183`.

## Governance boundary

The specification is reconstructed after execution and does not satisfy the immutable pre-execution C2 gate. Conservation remains a bounded computational observation and may partly reflect the partition definition. The result does not establish universal conservation, a causal residue law, implementation-independent validity, or external physical truth.
