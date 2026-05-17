# Falsification Protocols (MPF-DATA-MATH-005)

## 1. Purpose
Establish the mandatory falsification and null-model protocols required for every dataset campaign. These protocols ensure that observed signatures are not statistical artifacts or first-order distributional effects, but are instead structural products of the bound mathematical predictions.

## 2. Mandatory Controls
Every campaign must include:
- **shuffle_control**: Destroys relational order to test for non-random structure.
- **random_topology**: Substitutes local reach with global random links to test for locality bounds.
- **parameter_ablation**: Proves the irreducible necessity of core operators (e.g., $\epsilon, \rho$).
- **noise_baseline**: Measures the signal-to-noise threshold of the predicted signature.

## 3. Evidence Requirement
Failure to pass a mandatory falsification control results in the campaign being classified as `INCONCLUSIVE` or `NULL_SUPPORT`, regardless of the primary metric strength.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true
- **Required Statement**: Observed signatures are interpreted only through restricted local analog structure.

---
[Back to Governance Index](../README.md)
