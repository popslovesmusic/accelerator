# Typed engine-trace adapter specification — 2026-07-30

## Status

Proposed, non-canonical, C1 model-relative, blocked pending human review. No engine code or configuration was changed.

## Purpose

Define the minimum trace surface needed to test whether an approved engine preserves the distinction between S-stage pruning and Arb_A-stage arbitration under a declared tie policy.

## Fixture

Three candidates are supplied: two admissible candidates with equal minimum mismatch cost and one inadmissible lower-cost candidate. The adapter must preserve candidate identity and report whether the tie remains a set or is resolved by an explicit local policy.

## Required evidence

The adapter must emit candidate pools before and after S, removal reasons, Arb_A input/output, tie-policy ID, admissibility preservation, and runtime provenance. Acceptance requires the S output to be no larger than its input and Arb_A to consume exactly the S output pool.

## Current blocker

The inspected `ca_admissibility_sim_v1_cpp` and `graph_dynamics_sim_v1_cpp` wrappers expose aggregate `final_metrics` only. They do not expose typed candidate-level S/Arb_A traces, so engine corroboration cannot yet be claimed.

## Next action

Human review of the specification. If accepted, authorize a separate adapter implementation task with approved-tool execution and independent engine comparison.
