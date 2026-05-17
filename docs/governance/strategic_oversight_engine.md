# Strategic Oversight Engine (MPF-OPS-ESCALATE-008)

## 1. Purpose
Generate high-level strategic guidance for inquiry direction based on campaign outcomes, operational trends, and technical debt levels. This engine provides the human overseer with data-driven recommendations on where to focus resources (e.g., "Strengthen MT-002 support by running the Kuramoto C++ baseline").

## 2. Recommendation Classes
- **High-Value Campaigns**: Areas where new evidence would materially strengthen math-core stability.
- **Low-Value/High-Risk**: Areas with high counterexample dominance or persistent drift.
- **Resource Priority**: Guidance on whether to focus on equivalence emission, falsification expansion, or technical paper refinement.

## 3. Implementation
The `scripts/run_strategic_oversight_engine.py` script combines state data from across math, implementation, and evidence registries to produce prioritized recommendations.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Governance Index](../README.md)
