# Falsification Report: MPF_SIM_MECHANISM_ISOLATION_FAST_001

Outcome classification: `CONTIGUOUS_STABLE_REGION_DETECTED`

## Direction

This local Codex reproduction ran the notebook logic supplied by the user on the local workstation and wrote fresh metrics into `outputs/replications`.

## Results

- Parameter points: 192
- Seed-level run blocks: 1536
- Candidate stable points: 82
- Contiguous stable points: 57
- Stable fraction: 0.2969
- Runtime seconds: 103.79

## Best observed point

- Temperature: 0.15
- Lambda: 0.3514
- Eta: 0.25
- Mean relative improvement: 0.321487
- Seed consistency: 1.000
- Standardized effect: 1.287
- Mean paired-future JSD: 0.155397
- Finite-history win rate: 1.000
- Adjacent stable support: 3

## Decision

Next campaign: `MPF_SIM_INDEPENDENT_REPLICATION_001`

Reason: At least one temperature slice contains residue-supporting points with adjacent-grid stability.

## Governance

Exploratory computational evidence only. These results do not prove the framework, establish physical residue, or establish external physical validity.