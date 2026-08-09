# Autonomous Stop-Conditions (MPF-OPS-ESCALATE-005)

## 1. Purpose
Define and enforce the structural boundaries beyond which autonomous agents and orchestrators are no longer authorized to proceed. These conditions protect the framework's foundational integrity by preventing "runaway" automation from propagating corrupt evidence or inflationary claims.

## 2. Mandatory Stop Conditions
- **SC-001-EQUIV-FATAL**: Prevents continued use of high-performance engines that demonstrate systematic numerical divergence.
- **SC-002-GOVERNANCE-BREACH**: Immediately locks registries if an autonomous attempt is made to bypass scope disclaimers or claim-humility disclaimers.

## 3. Enforcement
These conditions are integrated into the `scripts/multi_sim_runner.py` and `scripts/math_program_validate.py` harnesses. A triggered stop condition requires an explicit `HUMAN_UNBLOCK` event in the `human_arbitration_queue.json`.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Governance Index](../README.md)
