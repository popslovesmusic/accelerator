# Notebook 19 Design: Exclusion Generates Residue

## Scope

Notebook 19 tests the proposed relation between exclusion of admissible distinction and residue generation in the finite relational organization model used by Notebook 18. It evaluates weak and strong admissibility separately and tests information, structural, and total residue criteria.

## Operational test

For each projection, the notebook records an exclusion vector and residue vector. Exclusion sufficiency is falsified by any exclusion-without-residue case. Exclusion necessity is falsified by any residue-without-exclusion case. The full biconditional survives only if both directions survive.

## Bounded execution

The archive reports seed `190019`, 1,217,346 total projection records, and 11,762 strongly admissible records. Source and target domains are finite sets of three domains with sizes 1 through 3. Target blocks are capped at 500 organizations and may use deterministic stratification.

## Direct result disposition

For strong admissibility, information and structural residue both falsify sufficiency and necessity. Total residue has no exclusion-without-residue cases, so sufficiency is not falsified, but 706 residue-without-exclusion cases falsify necessity; the biconditional is therefore falsified. The result is an association and operational counterexample analysis, not a causal or ontological result.

## Governance boundary

The experiment specification was reconstructed after execution and is not a pre-execution immutable gate. The result remains C2 bounded notebook evidence. It does not establish a universal exclusion law, a primitive causal law, implementation-independent validity, external physical truth, or C5/C6 status.
