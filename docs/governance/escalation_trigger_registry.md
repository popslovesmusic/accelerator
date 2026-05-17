# Escalation Trigger Registry (MPF-OPS-ESCALATE-002)

## 1. Purpose
Define the authoritative machine-readable triggers for system escalation. This registry ensures that the ecosystem's "stop and ask" logic is consistent, transparent, and governed by explicitly defined severity levels and intervention actions.

## 2. Authoritative Triggers
- **ET-001-COUNTER-DOMINANCE**: High risk of generic signatures or metric overbreadth. Requires human review of proxy metrics.
- **ET-002-EQUIV-FAIL**: Blocked certification. Requires investigation of implementation precision or algorithmic drift.
- **ET-003-CLAIM-DRIFT**: Critical violation of claim-humility disclaimers. Blocks autonomous technical paper emission.
- **ET-004-AGENT-CONFLICT**: Material disagreement between autonomous agents. Requires human arbitration.

## 3. Intervention Actions
- `HALT_CAMPAIGN_AND_ESCALATE`: Stop the specific evidence campaign immediately.
- `BLOCK_CERTIFICATION_AND_ESCALATE`: Prevent tool certification upgrades.
- `BLOCK_EMISSION_AND_ESCALATE`: Stop technical paper or result packet emission.
- `LOG_CONFLICT_AND_ESCALATE`: Continue but surface the contradiction prominently.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Governance Index](../README.md)
