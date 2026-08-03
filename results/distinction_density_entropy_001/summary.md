# Distinction-Density Entropy Campaign

Status: **FAIL**

This is a bounded model execution, not a physical validation.

| Regime | Max absolute error | Sign agreement | Path error | Reverse error |
|---|---:|---|---:|---:
| ideal_gas | 3.33066907388e-16 | True | 0 | 0 |
| two_level | 0.32006143957 | False | 0 | 0 |
| ising_2x2 | 1.92999063444 | False | 0 | 0 |

Controls:
- Uniform-density separation: FAIL (same entropy structure for finite state proxies).
- Permutation-control separation: FAIL (entropy is permutation invariant).

Interpretation: this execution does not support cross-regime correspondence under the frozen minimal operationalization. It demonstrates that a mathematically defined density distribution is not sufficient until its generation rule is specified with more structure.
