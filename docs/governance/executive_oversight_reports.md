# Executive Oversight Reports (MPF-OPS-ESCALATE-009)

## 1. Purpose
Emit high-level technical summaries for human systems governance. These reports provide a terminal overview of the ecosystem's health, risks, and progress, ensuring that oversight is built on standardized, non-inflationary data.

## 2. Mandatory Sections
Every report must include:
- **Ecosystem Status**: Terminal overall status (PASS/FAIL/STABLE).
- **Critical Risks**: Surface items from the `human_arbitration_queue.json`.
- **Human Attention Required**: Priority ranking of required judgments.
- **Campaign Progress**: Summary of active and completed evidence ladders.
- **Operational Debt**: Number of remaining C4 tool warnings.
- **Recommended Next Actions**: Derived from the Strategic Engine.

## 3. Implementation
The `scripts/generate_executive_oversight_reports.py` script aggregates data from all oversight registries to produce timestamped reports in `outputs/oversight_reports/`.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Governance Index](../README.md)
