# Campaign 006: External Entropy Comparison

## Scope

This C1 campaign compares Campaign 005's unchanged projection with independent ideal-gas, two-level, and exact 2×2 Ising entropy changes.

## Directly observed/defined

Candidate structural weights were generated before reference calculations and hash-locked. The frozen projection remained `log((target_weight + capacity)/(source_weight + capacity))`. No reference probabilities or entropy values entered candidate generation.

## Results

Entropy-direction agreement was 1.000 in all declared regimes: ideal gas (5 transitions), two-level (12), and 2×2 Ising (9). Mean absolute errors were 0.000000, 0.271341, and 0.369493 respectively. Thus directional correspondence was observed in these finite fixtures, while quantitative magnitude agreement was regime-limited.

## Leakage and verification

The candidate hash was recorded before references were calculated. Reference isolation and independent verification passed. The candidate was not revised after reference exposure.

## Inferred inside framework

The unchanged projection exhibits bounded directional correspondence across the tested fixtures. The result does not establish universal thermodynamic correspondence because magnitude error remains material in the two-level and Ising regimes.

## External resemblance (Analogy only)

The ideal-gas result resembles logarithmic volume scaling. This is an analogy to the tested formula, not proof of physical identity.

## What it does NOT prove

It does not prove entropy is distinction density, does not validate the projection universally, and does not establish physical RT dynamics.

## Failure modes / uncertainty

The accessibility rule is intentionally simple and was not fitted to references. The campaign covers finite declared fixtures only; no 3×3 Ising or broader topology transfer was tested.

## Status and next action

Status: `PARTIALLY_SUPPORTED_REGIME_LIMITED` (C1). Preserve the candidate and results. Next action: preregister a diagnosis of magnitude failure before any candidate revision.
