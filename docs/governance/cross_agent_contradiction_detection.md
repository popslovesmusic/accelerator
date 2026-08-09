# Cross-Agent Contradiction Detection (MPF-OPS-ESCALATE-006)

## 1. Purpose
Detect and govern instances where multiple autonomous agents produce materially incompatible findings, interpretations, or governance decisions. This detection ensures that the framework's multi-agent orchestration remains stable and that internal contradictions are never silently ignored or averaged out.

## 2. Detection Classes
- **claim_conflict**: Incompatible support verdicts (e.g., one agent claims `STRONG_SUPPORT`, another claims `FALSIFIED`).
- **metric_conflict**: Disagreement on raw numerical outputs for identical seeds/configs.
- **governance_conflict**: Differing interpretations of scope boundaries or disclaimer requirements.

## 3. Mandatory Action
Upon detection, the conflicting findings must be logged in the `registry/cross_agent_contradiction_registry.json` and a `HIGH` priority escalation must be sent to the `human_arbitration_queue.json`.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Governance Index](../README.md)
