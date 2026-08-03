# Campaign 006: External Entropy Comparison

## Scope
This bounded C1 campaign compares Campaign 005's unchanged projection with independent ideal-gas, two-level, and exact 2x2 Ising entropy changes.

## Directly observed/defined
Candidate structural weights were generated first and hash-locked. The frozen projection was `log((target_weight + capacity)/(source_weight + capacity))`. No reference probabilities or entropy values entered candidate generation.

## Results
Ideal-gas sign agreement: 1.000, mean absolute error: 0.000000. Two-level sign agreement: 1.000, mean absolute error: 0.271341. Ising sign agreement: 1.000, mean absolute error: 0.369493.

## Leakage and verification
The candidate hash was recorded before references were calculated. Isolation and independent verification passed. The candidate was not revised after reference exposure.

## Inferred inside framework
The unchanged projection shows a regime-limited comparison in these fixtures, with the ideal-gas construction matching direction. The broader thermodynamic correspondence question remains unresolved because the same frozen mapping was not quantitatively validated across all regimes.

## External resemblance (Analogy only)
The ideal-gas match resembles logarithmic volume scaling. This is an analogy to the tested formula, not proof of physical identity.

## What it does NOT prove
It does not prove entropy is distinction density, does not validate the projection universally, and does not establish physical RT dynamics.

## Failure modes / uncertainty
The candidate accessibility rule is intentionally simple and not fitted to references. The campaign is limited to the declared finite fixtures and should not be generalized beyond them.

## Status and next action
Status: `PARTIALLY_SUPPORTED_REGIME_LIMITED`. Preserve the candidate and results; next action is a preregistered diagnosis of the failed or regime-limited mappings before any revision.
